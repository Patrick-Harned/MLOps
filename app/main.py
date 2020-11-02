

if __name__ == "__main__":
    # %load_ext autoreload
    # %autoreload 2
    
    import sys, os
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # path, filename = os.path.split(dir_path)
    # if path not in sys.path:
    #     sys.path.append(path)

    import yaml

    from pipeline import Pipeline

    
    MODEL_METAPROPS_PATH = '../metaprops.yaml'
    with open(MODEL_METAPROPS_PATH) as f:
        metaprops = yaml.safe_load(f)
    _dir = os.path.dirname(os.path.abspath(MODEL_METAPROPS_PATH))
    metaprops['model_path'] = os.path.join(_dir, metaprops['model_path'])

    
    CP4D_CONFIG_PATH = '../cp4d_config.yaml'
    with open(CP4D_CONFIG_PATH) as f:
        cp4d_config = yaml.safe_load(f)



    pipeline = Pipeline(**cp4d_config, **metaprops)

    pipeline.specification()

    pipeline.set_connection()
    
    pipeline._init_cleanup()

    pipeline.set_project()
    
    pipeline.set_data()

    pipeline.set_namespace()

    pipeline.store_model()

    pipeline.deploy_model()

    pipeline.set_subscription()

    pipeline.run_quality_monitor()

    


