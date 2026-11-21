
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



def check_simulink_model(model_name: str):
    """檢查指定的 Simulink .slx 模型檔案是否存在。"""

    models_dir = Path(__file__).resolve().parent / "models"

    # 檢查模型資料夾
    if not models_dir.is_dir():
        return {
            "status": "error",
            "message": "models 資料夾不存在"
        }

    # 檢查輸入參數，避免不合法的路徑
    if (
        not isinstance(model_name, str)
        or not model_name.endswith(".slx")
        or not model_name[:-4].strip()
        or Path(model_name).name != model_name
        or "\\" in model_name
    ):
        return {
            "status": "error",
            "message": "無效的模型名稱，請輸入單一 .slx 檔名"
        }

    model_path = models_dir / model_name

    # 不接受符號連結，避免查詢模型目錄以外的檔案
    if model_path.is_symlink():
        return {
            "status": "error",
            "message": "不允許查詢符號連結模型"
        }

    exists = model_path.is_file()

    return {
        "status": "success",
        "model": model_name,
        "exists": exists,
        "message": (
            "找到指定模型" if exists else "找不到指定模型"
        )
    }
