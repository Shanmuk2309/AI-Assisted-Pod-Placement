from kfp import dsl
from kfp import compiler


@dsl.container_component
def train_component():

    return dsl.ContainerSpec(
        image="pod-placement-trainer:v10",

        command=["python"],

        args=[
            "train.py"
        ]
    )


@dsl.pipeline(
    name="pod-placement-training-pipeline"
)
def training_pipeline():

    train_component().set_display_name(
        "Train Placement Model"
    )


if __name__ == "__main__":

    compiler.Compiler().compile(
        pipeline_func=training_pipeline,
        package_path="pipeline.yaml"
    )

    print("Pipeline compiled successfully")