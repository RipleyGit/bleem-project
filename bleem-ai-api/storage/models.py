"""
数据库模型定义
支持 SQLite 和 MySQL
"""

# ==================== 用户表 ====================

# MySQL 用户表
USERS_TABLE_SQL_MYSQL = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    openid VARCHAR(100) NOT NULL UNIQUE COMMENT '微信用户唯一标识',
    nickname VARCHAR(100) COMMENT '用户昵称',
    avatar_url VARCHAR(500) COMMENT '用户头像 URL',
    gender TINYINT DEFAULT 0 COMMENT '性别: 0=未知, 1=男, 2=女',
    city VARCHAR(100) COMMENT '城市',
    province VARCHAR(100) COMMENT '省份',
    country VARCHAR(100) COMMENT '国家',
    location_id VARCHAR(50) COMMENT '和风天气 LocationID',
    latitude DECIMAL(10, 6) COMMENT '纬度',
    longitude DECIMAL(10, 6) COMMENT '经度',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后登录时间',
    INDEX idx_openid (openid)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='用户信息表';
"""

# SQLite 用户表
USERS_TABLE_SQL_SQLITE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    openid TEXT NOT NULL UNIQUE,
    nickname TEXT,
    avatar_url TEXT,
    gender INTEGER DEFAULT 0,
    city TEXT,
    province TEXT,
    country TEXT,
    location_id TEXT,
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# ==================== 衣物表 ====================

# MySQL 表结构（使用 AUTO_INCREMENT）
CLOTHES_TABLE_SQL_MYSQL = """
CREATE TABLE IF NOT EXISTS clothes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID（外键）',
    category VARCHAR(50) NOT NULL COMMENT '衣物分类：top, bottom, shoes',
    item VARCHAR(100) NOT NULL COMMENT '具体衣物名称，如 T恤、牛仔裤、运动鞋',
    style_semantics TEXT COMMENT '风格标签 JSON 数组，如 ["休闲", "正式", "运动"]',
    season_semantics TEXT COMMENT '季节标签 JSON 数组，如 ["春", "夏", "秋", "冬"]',
    usage_semantics TEXT COMMENT '使用场景 JSON 数组，如 ["通勤", "日常", "运动", "约会"]',
    color_semantics VARCHAR(50) COMMENT '颜色语义，如 深色系 / 浅色系 / 中性色',
    description TEXT COMMENT '一句话语义总结',
    image_filename VARCHAR(255) NOT NULL COMMENT '上传的图片文件名',
    image_data LONGBLOB COMMENT '图片二进制数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='智能衣橱衣物信息表';
"""

# SQLite 表结构（使用 AUTOINCREMENT）
CLOTHES_TABLE_SQL_SQLITE = """
CREATE TABLE IF NOT EXISTS clothes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,  -- top, bottom, shoes
    item TEXT NOT NULL,
    style_semantics TEXT,  -- JSON array
    season_semantics TEXT,  -- JSON array
    usage_semantics TEXT,  -- JSON array
    color_semantics TEXT,
    description TEXT,
    image_filename TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

# MySQL 索引
CLOTHES_INDEX_SQL_MYSQL = """
CREATE INDEX idx_clothes_category ON clothes(category);
"""

# SQLite 索引
CLOTHES_INDEX_SQL_SQLITE = """
CREATE INDEX IF NOT EXISTS idx_clothes_category ON clothes(category);
"""
# 
API_CONFIG_TABLE_SQL_MYSQL = """
CREATE TABLE `api_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `api_base` varchar(255) NOT NULL COMMENT '远程访问地址',
  `api_key` varchar(255) NOT NULL COMMENT '远程访问key',
  `api_type` varchar(255) NOT NULL COMMENT 'API类型',
  `model` varchar(255) DEFAULT NULL COMMENT '模型',
  `usage_count` tinyint(4) DEFAULT 0 COMMENT '使用次数',
  `del_flag` tinyint(4) DEFAULT 0 COMMENT '删除标志',
  `created_at` timestamp NULL DEFAULT current_timestamp() COMMENT '记录创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API 配置';
"""