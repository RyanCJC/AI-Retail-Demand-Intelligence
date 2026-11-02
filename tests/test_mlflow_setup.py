import mlflow


def test_mlflow_tracking():
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("retail-demand-intelligence")

    with mlflow.start_run():
        mlflow.log_param("setup_test", "successful")
        mlflow.log_metric("dummy_metric", 1.0)

    assert True