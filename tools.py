
from pathlib import Path


def list_simulink_models():
    """查詢專案內可用的 Simulink 模型。"""

    models_dir = Path(__file__).resolve().parent / "models"

    if not models_dir.exists():
        return {
            "status": "error",
            "message": "models 資料夾不存在"
        }

    models = sorted(
        file.name for file in models_dir.glob("*.slx")
        if file.is_file()
    )

    if not models:
        return {
            "status": "success",
            "models": [],
            "message": "目前沒有找到 Simulink 模型"
        }

    return {
        "status": "success",
        "models": models
    }
