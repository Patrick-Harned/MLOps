

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

    # to get abs path for paths relative to a file, when file is evaluated 
    # from other working dir.
    def abs_path(abs_root_file, path):
        _dir = os.path.dirname(os.path.abspath(abs_root_file))
        return os.path.normpath(os.path.join(_dir, path))


    MODEL_METAPROPS_PATH = abs_path(__file__, '../metaprops.yaml')
    try:   
        with open(MODEL_METAPROPS_PATH) as f:
            metaprops = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise type(e)('Model meta-properties yaml not found. File required for CI deployment.')
    metaprops['model_path'] = abs_path(MODEL_METAPROPS_PATH, metaprops['model_path'])

    
    CP4D_CONFIG_PATH = abs_path(__file__, '../cp4d_config.yaml')
    try:
        with open(CP4D_CONFIG_PATH) as f:
            cp4d_config = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise type(e)('CP4D platform config yaml not found. File required for CI deployment.')


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

    


