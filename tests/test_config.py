import tempfile

from sen_api.config import Config


def test_config():
    with tempfile.NamedTemporaryFile() as fp:
        file_name = fp.name.split('/')[-1]
        file_path = fp.name.replace(file_name, '')

        values = {
            'field1': 'sdkljfn',
            'field2': 'sadnsakd',
            'field3': 'stuff',
        }
        config = Config(base_path=file_path, config_file_name=file_name)
        config.write(section='test', values=values)

        for v in values.keys():
            config_val = config.get_value('test', v)
            assert config_val == values[v]

        assert config.get_value('test', 'not_present_value') is None
