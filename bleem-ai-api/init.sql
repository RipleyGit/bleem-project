DROP TABLE IF EXISTS aiwardrobe.clothes;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS aiwardrobe 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE aiwardrobe;

-- 创建衣物表
CREATE TABLE IF NOT EXISTS clothes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL COMMENT '衣物分类：top, bottom, shoes',
    item VARCHAR(100) NOT NULL COMMENT '具体衣物名称，如 T恤、牛仔裤、运动鞋',
    style_semantics TEXT COMMENT '风格标签 JSON 数组，如 ["休闲", "正式", "运动"]',
    season_semantics TEXT COMMENT '季节标签 JSON 数组，如 ["春", "夏", "秋", "冬"]',
    usage_semantics TEXT COMMENT '使用场景 JSON 数组，如 ["通勤", "日常", "运动", "约会"]',
    color_semantics VARCHAR(50) COMMENT '颜色语义，如 深色系 / 浅色系 / 中性色',
    description TEXT COMMENT '一句话语义总结',
    image_filename VARCHAR(255) NOT NULL COMMENT '上传的图片文件名',
    image_data LONGBLOB COMMENT '图片二进制数据',
    del_flag TINYINT DEFAULT 0 COMMENT '删除标志',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='智能衣橱衣物信息表';

-- 创建索引
CREATE INDEX idx_clothes_category ON clothes(category);

-- 可选：根据实际查询需求，可以添加更多索引
-- CREATE INDEX idx_clothes_created_at ON clothes(created_at);
-- CREATE INDEX idx_clothes_item ON clothes(item(50));

-- API 配置
CREATE TABLE IF NOT EXISTS api_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_base VARCHAR(255) NOT NULL COMMENT '远程访问地址',
    api_key VARCHAR(255) NOT NULL COMMENT '远程访问key',
    api_type VARCHAR(255) NOT NULL COMMENT 'API类型',
    model VARCHAR(255) COMMENT '模型',
    usage_count TINYINT DEFAULT 0 COMMENT '使用次数',
    del_flag TINYINT DEFAULT 0 COMMENT '删除标志',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='API 配置';