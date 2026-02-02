def match_rule(rule, post):
    """
    rule: 設定檔裡的規則 (str 或 dict)
    post: 文章物件 (包含 title, push_count)
    """
    title = post['title']
    push_count = post.get('push_count', 0)

    # 1. 簡單規則 (只比對標題)
    if isinstance(rule, str):
        return rule in title

    # 2. 進階規則
    elif isinstance(rule, dict):
        
        # 條件 A: 推文數門檻 (如果沒設定 min_push，預設為 0，即過濾噓文)
        required_push = rule.get("min_push", 0)
        if push_count < required_push:
            return False

        # 條件 B: 關鍵字邏輯
        # 如果規則裡完全沒有關鍵字相關設定(AND/include/exclude)，代表這條規則是「純推文數規則」
        # 例如: {"min_push": 99} -> 只要推文夠就過
        has_keyword_condition = ("AND" in rule) or ("include" in rule) or ("exclude" in rule)
        
        if not has_keyword_condition:
            return True # 沒設關鍵字條件，且上面推文數已過 -> 命中

        # 條件 C: 複合關鍵字比對
        if "AND" in rule:
            if not all(k in title for k in rule["AND"]): return False
            
        if "include" in rule: # 支援單一字串
             if rule["include"] not in title: return False
             
        if "exclude" in rule:
            if rule["exclude"] in title: return False

        return True

    return False

def is_interested(post, source_config, global_config):
    """
    判斷文章是否符合興趣
    """
    title = post['title']
    
    # 1. 黑名單檢查 (優先過濾)
    all_blacklists = global_config.get('blacklist', []) + source_config.get('blacklist', [])
    for rule in all_blacklists:
        # 只看標題
        if isinstance(rule, str) and rule in title: return False
        if isinstance(rule, dict) and "include" in rule and rule["include"] in title: return False

    # 2. 關鍵字與推文數檢查
    # 合併 全域關鍵字 + 看板專屬關鍵字
    all_keywords = global_config.get('keywords', []) + source_config.get('keywords', [])
    
    # 如果完全沒設定關鍵字，也沒設定推文門檻，就預設不抓 (除非用 [""] 全抓)
    if not all_keywords:
        return False

    for rule in all_keywords:
        # 將整包 post 丟進去比對
        if match_rule(rule, post):
            return True

    return False