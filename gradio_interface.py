from haystack import Pipeline
from haystack.core.serialization import DeserializationCallbacks
from typing import Type, Dict, Any
import gradio as gr


def component_pre_init_callback(component_name: str, component_cls: Type, init_params: Dict[str, Any]):
    # This function gets called every time a component is deserialized.
    if component_name == "cleaner":
        assert "DocumentCleaner" in component_cls.__name__
        # Modify the init parameters. The modified parameters are passed to
        # the init method of the component during deserialization.
        init_params["remove_empty_lines"] = False
        print("Modified 'remove_empty_lines' to False in 'cleaner' component")
    else:
        print(f"Not modifying component {component_name} of class {component_cls}")


# Load the pipeline from the YAML file
def load_pipeline_from_yaml(yaml_file_path):
    with open(yaml_file_path, "r") as stream:
        pipeline_yaml = stream.read()
    return Pipeline.loads(pipeline_yaml, callbacks=DeserializationCallbacks(component_pre_init_callback))


# Function to interact with the pipeline
def ask_question(question, pipeline):
    answer = pipeline.run({
        "text_embedder": {"text": question},
        "prompt_builder": {"question": question},
        "answer_builder": {"query": question}
    })
    return answer['answer_builder']['answers'][0].data


# Load the pipeline (modify path if necessary)
my_pipeline = load_pipeline_from_yaml('./pipeline.yml')

# Set up Gradio interface with Blocks layout
with gr.Blocks() as interface:
    gr.Markdown("# Wire RAG Documentation")  # Title
    gr.Markdown("Ask a question and get a documentation answer.")

    input_box = gr.Textbox(label="Ask your question:", placeholder="Type your question here...", lines=1)
    output_box = gr.Markdown(label="Answer:")  # Output field

    submit_btn = gr.Button("Submit")  # Submit button
    submit_btn.click(fn=lambda question: ask_question(question, my_pipeline), inputs=input_box, outputs=output_box)

# Launch the Gradio app with sharing
interface.launch(share=True)
