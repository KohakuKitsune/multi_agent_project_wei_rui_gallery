import gradio as gr
import os
import uuid
import shutil
from agents.design_coordinator import design_coordinator
from agents.image_generator import image_generator
from agents.feasibility_planner import feasibility_planner
from crewai import Crew, Task
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = "uploaded_images"
ORDER_FOLDER = "orders"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ORDER_FOLDER, exist_ok=True)


# Global context
user_inputs_cache = {}
generated_images = {}

# Mapping dictionaries (Chinese to English)
style_map = {
    "中式畫框": "Chinese frame",
    "西式畫框": "Western frame"
}

kind_map = {
    "内框": "Inner frame",
    "外框": "Outer frame",
    "底板": "Backboard"
}

material_map = {
    "古典": "Classical",
    "木": "Wood",
    "白木": "White wood",
    "黑木": "Black wood",
    "2k": "2K"
}

paint_color_map = {
    "灰色": "Gray",
    "咖啡色": "Brown",
    "黑色": "Black",
    "金色": "Gold",
    "銀色": "Silver",
    "自訂": "Custom"
}

def submit_request(image_path, image_desc, width, height, style, kind, material_choice, paint_choice, custom_color, extra_notes):
    global generated_images, user_inputs_cache

    # Convert to English
    paint_color = custom_color if paint_choice == "自訂" else paint_color_map.get(paint_choice, paint_choice)
    style_en = style_map.get(style, style)
    kind_en = kind_map.get(kind, kind)
    material_en = material_map.get(material_choice, material_choice)

    # Construct English user request
    full_user_request = f"""
    Frame Style: {style_en}
    Frame Type: {kind_en}
    Frame Dimensions: {width}cm x {height}cm
    Frame Material: {material_en}
    Paint Color: {paint_color}
    Additional Notes: {extra_notes}
    """
    print(full_user_request)
    print(image_path)

    if image_desc and not image_path: 
        task1 = Task(
            description="""
                Generate a detailed image prompt based on the user's description.
                Description: {image_desc}
                Frame Material: {material_choice}
            """,
            expected_output="Optimized prompt for image generation",
            agent=design_coordinator
        )

        task2 = Task(
            description="""
                Using the prompt output from task 1, generate an image.
            """,
            expected_output="File path to generated image",
            agent=image_generator,
            context=[task1]
        )

        task3 = Task(
            description="""
                Frame the generated image at {generated_image}  using {material_choice} material.
            """,
            expected_output="File path to framed image",
            agent=image_generator,
        )
        crew = Crew(agents=[design_coordinator, image_generator], tasks=[task1, task2, task3], verbose=True)

        result = crew.kickoff(inputs={
            "image_desc": image_desc,
            "material_choice": material_en,
            "generated_image": "D:\\Multi-Agent-Project\\outputs\\generate.png"
        })

    elif image_path:
        print("Execute 1")
        filename = os.path.basename(image_path)
        saved_path = os.path.join(UPLOAD_FOLDER, filename)
        shutil.copy(image_path, saved_path)  # Move from temp to permanent folder
        image_path = saved_path  # Update path for use in Crew task

        print(image_path)

        task1 = Task(
            description="""
                Frame the uploaded image at {image_path} using {material_choice} material.
            """,
            expected_output="File path to framed image",
            agent=image_generator
        )

        crew = Crew(agents=[image_generator], tasks=[task1], verbose=True)
        result = crew.kickoff(inputs={
            "image_path": image_path,
            "material_choice": material_en
        })

    else:
        return None, "❌ 請提供圖片或圖片描述之一。"

    print("[DEBUG] Crew result:", result)
    print("[DEBUG] Type of result:", type(result))

    framed_image = result

    generated_images["final"] = framed_image
    user_inputs_cache = {
        "image_path": image_path,
        "image_desc": image_desc,
        "width": width,
        "height": height,
        "style": style_en,
        "kind": kind_en,
        "paint_color": paint_color,
        "extra_notes": extra_notes,
        "final_image": framed_image,
        "full_prompt": full_user_request
    }

    return "D:\\Multi-Agent-Project\\outputs\\output.png"

def confirm_order():
    final_img = generated_images.get("final")
    if not final_img:
        return "❌ 尚未生成有效圖片，請先送出需求。"

    evaluation_prompt = f"""
    Feasibility Evaluation:
    - Image Path: {final_img}
    - Dimensions: {user_inputs_cache['width']}cm x {user_inputs_cache['height']}cm
    - Style: {user_inputs_cache['style']}
    - Type: {user_inputs_cache['kind']}
    - Paint Color: {user_inputs_cache['paint_color']}
    - Notes: {user_inputs_cache['extra_notes']}
    """

    task = Task(
        description="Feasibility check and save order",
        agent=feasibility_planner,
        expected_output="Evaluation result",
        input={"evaluation_request": evaluation_prompt}
    )

    crew = Crew(agents=[feasibility_planner], tasks=[task], verbose=True)
    result = crew.kickoff(inputs={"evaluation_request": evaluation_prompt})

    order_id = uuid.uuid4().hex[:8]
    order_path = os.path.join(ORDER_FOLDER, f"order_{order_id}.txt")
    with open(order_path, "w", encoding="utf-8") as f:
        f.write(f"訂單ID: {order_id}\n")
        f.write(f"圖片路徑: {final_img}\n")
        for k, v in user_inputs_cache.items():
            f.write(f"{k}: {v}\n")
        f.write(f"評估結果:\n{result}")

    return f"✅ 訂單已完成並儲存於：{order_path}"

def toggle_custom_color(choice):
    return gr.update(visible=(choice == "自訂"))

def clear_image_if_desc(desc):
    return gr.update(value=None, interactive=False)

def clear_desc_if_image(image):
    return gr.update(value="", interactive=False)

with gr.Blocks() as demo:
    gr.Markdown("## 🎨 畫框設計訂單系統")

    with gr.Row():
        image_input = gr.Image(type="filepath", label="上傳圖片")
        image_desc = gr.Textbox(label="圖片描述（可選）")

    image_input.change(fn=clear_desc_if_image, inputs=image_input, outputs=image_desc)
    image_desc.change(fn=clear_image_if_desc, inputs=image_desc, outputs=image_input)

    with gr.Row():
        width_input = gr.Textbox(label="畫框寬度 (cm)")
        height_input = gr.Textbox(label="畫框高度 (cm)")
        style_input = gr.Radio(["中式畫框", "西式畫框"], label="畫框樣式")
        kind_input = gr.Radio(["内框", "外框", "底板"], label="畫框種類")
        material_choice = gr.Radio(["古典", "木", "白木", "黑木", "2k"], label="畫框材質")
        paint_color_choice = gr.Radio(["灰色", "咖啡色", "黑色", "金色", "銀色", "自訂"], label="噴漆顏色")
        custom_color_input = gr.Textbox(label="自訂顏色（若選擇自訂）", visible=False)
        paint_color_choice.change(fn=toggle_custom_color, inputs=paint_color_choice, outputs=custom_color_input)
        notes_input = gr.Textbox(label="補充說明")

    submit_btn = gr.Button("送出需求")
    image_output = gr.Image(label="生成結果預覽")
    finalize_btn = gr.Button("✅ 確認送出訂單")
    status_output = gr.Textbox(label="訂單狀態與詳情", lines=8)

    submit_btn.click(
        fn=submit_request,
        inputs=[image_input, image_desc, width_input, height_input, style_input, kind_input,
                material_choice, paint_color_choice, custom_color_input, notes_input],
        outputs=[image_output]
    )

    finalize_btn.click(
        fn=confirm_order,
        inputs=[],
        outputs=status_output
    )

if __name__ == "__main__":
    demo.launch(debug=True)
