# Led Wall Calibration

> Tools for Led Wall calibration

| 属性 | 值 |
|---|---|
| 中文名 | LED 墙校准 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `LedWallCalibration` (Runtime), `LedWallCalibrationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration) | |

## 总体用途

该插件提供用于 LED 墙校准的工具集。基于 `CameraCalibrationCore` 和 `OpenCV`，通过相机拍摄 LED 墙上的标记图案（如棋盘格或圆点），计算 LED 墙在物理空间中的位置、朝向和像素映射关系，从而实现虚拟摄像机与真实 LED 墙的对齐。适用于虚拟制片、XR 拍摄等需要精准 LED 背投校准的场景。

## 模块列表

| 模块 | 类型 | 一句话总结 | 文档 |
|---|---|---|---|
| `LedWallCalibration` | Runtime | 核心校准算法、数据结构与运行时数据管理 | [LedWallCalibration](LedWallCalibration.md) |
| `LedWallCalibrationEditor` | Editor | 编辑器 UI、校准工具面板和流程控制 | [LedWallCalibrationEditor](LedWallCalibrationEditor.md) |

## 使用场景

- 虚拟制片场景中，需要将真实 LED 墙的物理像素与虚幻引擎中的虚拟相机内参、外参对齐。
- 舞台搭建后，使用相机拍摄 LED 墙上显示的棋盘格或圆点图案，自动计算出 LED 墙的中心、旋转和缩放。
- 配合 nDisplay 或 ICVFX 系统，实现 LED 墙的精确投射校正，消除视觉错位。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | 相机内参标定与透视解算基础 |
| `OpenCV` | 图像特征检测（如棋盘格角点检测） |

其他为常见依赖（Core、Engine、Slate 等）。

## 维护状态

### 近期更新

- 2025-05-21 `269aeb1b` — Replaced bool arguments with EFindObjectFlags（改进枚举参数）
- 2023-08-29 `3a058044` — CameraCalibration: Refactor opencv implementation details out of the camera calibration plugins（重构，将 OpenCV 实现从相机校准插件中分离）
- 2023-07-19 `574e8e6e` — Add a ShortName to modules that generated paths over the 200 chars limit（修复长路径问题）
- 2023-04-15 `933348f8` — Use the FMessageDialog overloads that pass the optional title by-value（消息对话框参数优化）
- 2023-01-27 `f9121212` — Added generated.h includes and updated enums to have underlying types（初始提交，基础结构）

### 维护评价

该插件创建于 2023 年初，2025 年仍有代码优化提交，保持活跃维护。作为实验性功能（`IsBetaVersion=true`），API 可能在未来版本发生变动，但核心功能基本稳定。推荐在虚拟制片项目中使用，注意需手动启用并确保依赖插件（CameraCalibrationCore、OpenCV）已安装。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration)
- [LedWallCalibration 模块文档](LedWallCalibration.md)
- [LedWallCalibrationEditor 模块文档](LedWallCalibrationEditor.md)