# Led Wall Calibration

> Tools for Led Wall calibration（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | LED 墙校准工具 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具） |
| 模块 | `LedWallCalibration` (Runtime), `LedWallCalibrationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-08-03 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration) | |

## 用途
该插件为虚拟制作（Virtual Production）工作流中的 LED 墙提供了校准工具集。其核心功能是解决相机与 LED 墙之间的几何与颜色映射问题。通过利用 OpenCV 库，它能够标定相机的内参和相对 LED 墙的外参，从而生成查找表（LUT）以校正拍摄到的画面，确保虚拟背景与摄像机运动的精确匹配，是虚拟制作片场不可或缺的调试与设置工具。

## 使用场景
- 你在使用 LED 墙进行虚拟拍摄，需要确保摄像机移动时，LED 墙上显示的虚拟背景透视关系正确，不会出现错位或扭曲。
- 你需要校准 LED 墙的颜色输出，使其与摄像机拍摄的画面在色彩上保持一致，避免后期需要大量的颜色校正工作。

## 蓝图用法
该插件主要通过编辑器内的工具面板进行操作，蓝图可直接调用的通用节点较少。其核心功能集成在 `LedWallCalibrationEditor` 模块提供的编辑器工具中。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| （主要通过编辑器菜单和面板操作） | 访问校准工具、执行相机标定、生成校准数据。 | `ULedWallCalibrationToolkit` (工具面板管理器) |

### 使用示例（蓝图描述）
该插件的典型使用不依赖于蓝图图表连接，而是通过编辑器内的专用界面：
1.  在编辑器主菜单或虚拟制片工具栏中，找到并打开“LED Wall Calibration”工具面板。
2.  在面板中配置 LED 墙的几何参数（如尺寸、分辨率）和相机设置。
3.  运行标定流程，插件会引导你拍摄一组特定图案，并利用 OpenCV 进行计算。
4.  生成校准结果（几何映射、颜色校正 LUT），并将其应用到场景中的 LED 墙 Actor 或相关渲染设置上。

## C++ 用法
主要面向编辑器扩展和自定义校准流程的开发者。核心逻辑位于 `LedWallCalibration` Runtime 模块和 `LedWallCalibrationEditor` Editor 模块中。

### 头文件引入
```cpp
#include "LedWallCalibration.h"
// 对于编辑器扩展
#include "LedWallCalibrationEditor.h"
```

### 基本用法
该插件的功能主要通过其提供的编辑器工具使用，运行时直接调用 C++ API 的场景较少。详细的模块 API 和数据结构请参考各模块文档。
- **Runtime 模块 (`LedWallCalibration`)**: 包含核心校准数据结构和算法实现（如相机标定、LUT 生成）。
- **Editor 模块 (`LedWallCalibrationEditor`)**: 提供用户界面、工具面板、资产编辑器扩展等，是用户交互的主要入口。

### 进阶用法
可以基于 `LedWallCalibration` 模块提供的核心类（如相机模型、校准数据类），在自定义的虚拟制片管线或工具中集成校准功能。

## Demo 示例
一个典型的虚拟制作 LED 墙校准工作流如下：
1.  **准备**: 在场景中放置代表 LED 墙的平面 Actor，并设置其物理尺寸。
2.  **配置**: 打开 `LedWallCalibrationEditor` 提供的工具面板，关联目标 LED 墙 Actor。
3.  **标定**: 使用面板上的功能，让程序生成校准图案，用实际拍摄的摄像机拍摄这些图案。
4.  **计算**: 插件利用 OpenCV 分析图像，计算相机参数和 LED 墙的位置关系。
5.  **应用**: 将计算结果（几何映射矩阵、颜色校正 LUT）应用到渲染管线中，实时校正 LED 墙的输出。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | 提供基础的相机校准框架、资产类型和数据接口。 |
| `OpenCV` | 提供核心的计算机视觉库，用于执行相机标定等数学运算。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统 UE_LOG 日志宏迁移到新的 UE_LOGF 格式。 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新过时的构建版本配置设置。 |
| 2025-05-21 | `269aeb1b` | Replaced bool arguments with EFindObjectFlags. | 代码重构：将布尔参数替换为 EFindObjectFlags 枚举，使逻辑更清晰。 |
| 2023-08-29 | `3a058044` | CameraCalibration: Refactor opencv implementation details out of the camera calibration plugins and ... | 对相机校准相关插件的 OpenCV 实现细节进行了重构，提高了代码组织性。 |
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules that generated paths over the 200 chars limit and a few modules that were ... | 为路径过长的模块添加了短名称，解决了路径长度限制问题。 |

### 维护评价
该插件创建于 2021 年，已超过 5 年，属于“老古董”级别。从近期提交记录看，其更新主要集中在**编译兼容性修复**（如日志宏迁移、构建设置更新）和**底层代码重构**（如参数类型替换、模块路径优化），自 2023 年 8 月的 OpenCV 实现重构后，未见有新功能或针对虚拟制片流程的实质性改进。考虑到其仍标记为 `IsBetaVersion` 且 `EnabledByDefault=false`，表明它一直处于实验性状态，并未成为稳定的核心功能。**不推荐用于要求高稳定性的正式生产环境**，但可以作为研究虚拟制片校准技术的参考。最近一次非维护性更新停留在 2023 年，距离现在已经超过 2 年，表明**维护不活跃，存在被废弃的风险**。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration)
- 官方文档链接未提供
- [LedWallCalibration 模块文档](LedWallCalibration.md)
- [LedWallCalibrationEditor 模块文档](LedWallCalibrationEditor.md)