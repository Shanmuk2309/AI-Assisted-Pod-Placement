from kfp import dsl
from kfp import compiler


@dsl.container_component
def train_xgb_component():

    return dsl.ContainerSpec(

        image="pod-placement-xgboost-trainer:v1",

        command=["python"],

        args=[
            "train.py"
        ]
    )


@dsl.pipeline(
    name="pod-placement-xgboost-training-pipeline"
)
def training_pipeline():

    train_xgb_component().set_display_name(
        "Train XGBoost Model"
    )


if __name__ == "__main__":

    compiler.Compiler().compile(
        pipeline_func=training_pipeline,
        package_path="xgb_pipeline.yaml"
    )

    print("XGBoost Pipeline compiled successfully")