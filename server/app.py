# Version: 1.0.6 - Ultra Custom Dashboard
import sys, os
import json
from datetime import datetime
import gradio as gr
sys.path.append(os.getcwd())

from openenv.core.env_server.http_server import create_app
from src.models import EmailAction, EmailObservation
from src.env import EmailTriageEnv

def email_gradio_builder(web_manager, action_fields, metadata, is_chat_env, title, quick_start_md):
    """Custom Gradio Builder to match the professional demo layout."""
    
    with gr.Blocks(title=title) as demo:
        gr.Markdown(f"# {title}")
        
        with gr.Row():
            # LEFT COLUMN: Action Panel
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("### 🤖 HumanAgent Interface")
                    with gr.Group():
                        gr.Markdown("**Take Action**")
                        # Generate inputs based on action fields
                        step_inputs = []
                        for field in action_fields:
                            name = field["name"]
                            label = name.replace("_", " ").title()
                            choices = field.get("choices")
                            if choices:
                                inp = gr.Dropdown(choices=choices, label=label, value=choices[0])
                            elif field.get("type") == "number":
                                inp = gr.Number(label=label, value=0)
                            else:
                                inp = gr.Textbox(label=label, placeholder=f"Enter {label}...")
                            step_inputs.append(inp)
                        
                        step_btn = gr.Button("Step", variant="primary")
                
                with gr.Group():
                    with gr.Row():
                        reset_btn = gr.Button("Reset Environment", variant="secondary")
                        get_state_btn = gr.Button("Get State", variant="secondary")
                    
                with gr.Group():
                    gr.Markdown("### 📊 Current State")
                    status_text = gr.Markdown("Status: *Ready*")
                    state_display = gr.JSON(label="State Details")

            # RIGHT COLUMN: Observation & History
            with gr.Column(scale=2):
                gr.Markdown("### 🔍 State Observer")
                with gr.Accordion("Current Observation", open=True):
                    obs_display = gr.JSON(label="Latest Data")
                    reward_display = gr.Number(label="Last Reward", interactive=False)
                
                with gr.Accordion("Action History", open=True):
                    history_log = gr.HTML(value="<div style='color:gray'>No actions yet...</div>")

        # History Tracker Logic
        history_state = gr.State([])

        def update_history(history, action, obs, reward, done):
            timestamp = datetime.now().strftime("%H:%M:%S")
            entry = f"""
            <div style='border-left: 4px solid #2196F3; padding: 10px; margin: 10px 0; background: #f9f9f9;'>
                <small style='color:gray'>{timestamp} (Step {len(history)+1})</small><br>
                <b>Action:</b> {action}<br>
                <b>Observation:</b> {list(obs.keys())}<br>
                <b style='color:{'green' if reward > 0 else 'red'}'>Reward: {reward}</b> {'[DONE]' if done else ''}
            </div>
            """
            history.insert(0, entry)
            return history, "".join(history)

        # Event Handlers
        async def on_reset():
            data = await web_manager.reset_environment()
            return (
                data["observation"], 
                0.0, 
                "Status: **Running**", 
                data,
                [], 
                "<div style='color:gray'>Environment Reset.</div>"
            )

        async def on_step(*args):
            # values are in args
            action_data = {}
            for i, field in enumerate(action_fields):
                action_data[field["name"]] = args[i]
            
            try:
                data = await web_manager.step_environment(action_data)
                # Update history
                curr_history = args[-1] # Gr.State
                new_hist, hist_html = update_history(
                    curr_history, 
                    action_data, 
                    data["observation"], 
                    data.get("reward", 0), 
                    data.get("done", False)
                )
                
                return (
                    data["observation"], 
                    data.get("reward", 0), 
                    f"Status: {'**Done**' if data.get('done') else '**Running**'}",
                    data,
                    new_hist,
                    hist_html
                )
            except Exception as e:
                return {}, 0, f"Error: {str(e)}", {}, args[-1], "".join(args[-1])

        def on_get_state():
            return web_manager.get_state()

        reset_btn.click(fn=on_reset, outputs=[obs_display, reward_display, status_text, state_display, history_state, history_log])
        step_btn.click(fn=on_step, inputs=step_inputs + [history_state], outputs=[obs_display, reward_display, status_text, state_display, history_state, history_log])
        get_state_btn.click(fn=on_get_state, outputs=[state_display])

    return demo

# Force Enable the Web UI internally to avoid 404s
os.environ["ENABLE_WEB_INTERFACE"] = "true"

# Create the App with Custom Builder
app = create_app(
    EmailTriageEnv,
    EmailAction,
    EmailObservation,
    env_name="Email Triage Agent",
    max_concurrent_envs=1,
    gradio_builder=email_gradio_builder
)

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
