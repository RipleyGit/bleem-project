/*
 Navicat Premium Data Transfer

 Source Server         : 121.41.30.183
 Source Server Type    : MySQL
 Source Server Version : 110803
 Source Host           : 121.41.30.183:6033
 Source Schema         : aiwardrobe

 Target Server Type    : MySQL
 Target Server Version : 110803
 File Encoding         : 65001

 Date: 06/02/2026 10:01:24
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for api_config
-- ----------------------------
DROP TABLE IF EXISTS `api_config`;
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API 配置';

-- ----------------------------
-- Records of api_config
-- ----------------------------
BEGIN;
INSERT INTO `api_config` VALUES (1, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'sk-148840d44c25411c9cabd4ae380c6fa6', 'llm', 'qwen3-omni-flash', 0, 0, '2025-12-30 10:45:00');
INSERT INTO `api_config` VALUES (2, 'https://api.remove.bg/v1.0/removebg', 'U7SQcG2xEUtdFNfsUSmUAHjC', 'removebg', 'removebg', 3, 0, '2025-12-30 11:22:17');
INSERT INTO `api_config` VALUES (3, 'https://n557rkkjy3.re.qweatherapi.com/geo/v2/city/lookup', 'afc3d9074f244722932cdf2e94b6a84c', 'qweather', NULL, 0, 0, '2025-12-30 11:23:29');
INSERT INTO `api_config` VALUES (4, 'https://api.remove.bg/v1.0/removebg', 'tpHgusw5yWLaTk4xnmoZPCeA', 'removebg', 'removebg', 3, 0, '2025-12-30 11:22:17');
INSERT INTO `api_config` VALUES (5, 'https://api.remove.bg/v1.0/removebg', 'KkwMAWTjCA9k8Nkzvb8ezfra', 'removebg', 'removebg', 2, 0, '2026-01-06 22:34:58');
INSERT INTO `api_config` VALUES (6, 'https://api.remove.bg/v1.0/removebg', 'F37Bcm7y8rCnJtVXQSqrB3kJ', 'removebg', 'removebg', 2, 0, '2026-01-06 22:39:10');
INSERT INTO `api_config` VALUES (7, 'https://api.remove.bg/v1.0/removebg', '5tJqReRjkjq11QkpaRA9si2y', 'removebg', 'removebg', 1, 0, '2026-01-06 22:45:16');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
