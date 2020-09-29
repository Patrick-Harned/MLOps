from pipeline.model import model

def model_runtime_manager(model):
    import subprocess, sys
    try:
        model = model.model()
    except(ModuleNotFoundError) as error:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', error.name])
        model = model.model()

    return model

