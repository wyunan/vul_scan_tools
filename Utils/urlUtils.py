from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import json
from copy import deepcopy
from jsonpath_ng import jsonpath, parse


def payload_replace_query_params(init_url: str, payload_list: list) -> list:
    try:
        end_payload_url = []
        parsed_url = urlparse(init_url)
        query_params = parse_qs(parsed_url.query)
        for payload in payload_list:
            for k, v in query_params.items():
                # 将选定参数值替换为payload
                query_params[k] = payload
                # 对参数进行编码
                new_query_params = urlencode(query_params, doseq=True)
                # 生成新的query参数组合
                new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params,
                                      new_query_params, parsed_url.fragment))
                end_payload_url.append(new_url)
                # 还原原来的值，轮训到下一步替换下一个参数
                query_params[k] = v

        return end_payload_url
    except Exception as e:
        raise e


def payload_replace_body_params(content_type: str, data: str, payload_list: list) -> list:
    try:
        if "application/x-www-form-urlencoded" in content_type:
            pass

        elif "application/json" in content_type:
            # 函数：递归遍历JSON对象，找到所有待替换的位置
            # 找到所有可以替换的 JSONPath 表达式
            def find_all_paths(json_obj):
                """找到所有可以替换的 JSONPath 表达式"""
                jsonpath_expr = parse('$..*')
                paths = [match.full_path for match in jsonpath_expr.find(json_obj) if
                         not isinstance(match.value, (dict, list))]
                return paths

            # 替换特定值并生成多个 JSON
            def replace_value_and_generate_json(json_template, paths, payload_list: list):
                json_outputs = []
                for payload in payload_list:
                    for path in paths:
                        new_json = deepcopy(json_template)
                        jsonpath_expr = parse(str(path))
                        for match in jsonpath_expr.find(new_json):
                            parent = match.context.value
                            # 在这里要确保替换的值是正确的键
                            if hasattr(match.path, 'left') and match.path.left:
                                final_key = match.path.left.fields[0] if isinstance(match.path.left,
                                                                                    jsonpath.Child) else match.path.left
                                parent[final_key] = payload
                            else:
                                final_key = match.path.fields[0] if isinstance(match.path,
                                                                               jsonpath.Child) else match.path
                                parent[final_key] = payload
                        json_outputs.append(new_json)
                return json_outputs

            # 查找所有可以替换的路径
            # 解析JSON对象
            data_json = json.loads(data)
            paths = find_all_paths(data_json)
            # 替换特定值并生成多个 JSON
            json_list = replace_value_and_generate_json(data_json, paths, payload_list)
            print(json_list)
            return json_list
        else:
            return False
    except Exception as e:
        raise e
