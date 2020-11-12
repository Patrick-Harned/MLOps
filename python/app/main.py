

if __name__ == "__main__":
    # %load_ext autoreload
    # %autoreload 2
    
    #import sys, os
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # path, filename = os.path.split(dir_path)
    # if path not in sys.path:
    #     sys.path.append(path)

    import sys
    import os
    
    import yaml

    from pipeline import Pipeline

    def abs_path(root_file, path):
        '''get abs path of file relative to parent of a reference file'''
        _dir = os.path.dirname(os.path.abspath(root_file))
        return os.path.normpath(os.path.join(_dir, path))


    CONFIG_PATH = abs_path(__file__, '../config.yaml')
    try:   
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise type(e)(f'{e.filename} does not exist. Config file required to run pipeline.')
    config['Model']['model_path'] = abs_path(CONFIG_PATH, config['Model']['model_path'])


    pipeline = Pipeline(**config['CP4D'], **config['Model'])

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

    


