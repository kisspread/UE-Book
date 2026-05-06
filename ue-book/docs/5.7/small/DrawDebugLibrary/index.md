# Draw Debug Library

> A library of common debug drawing functions.

| 属性 | 值 |
|---|---|
| 中文名 | 调试绘制库 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DrawDebugLibrary` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DrawDebugLibrary) | |

## 用途

该插件提供了一组通用的调试绘制函数，旨在简化蓝图中绘制点、线、形状等调试信息的流程。当前处于实验阶段（版本号 0.1），仅暴露了基础的日志等级枚举和点样式结构体，完整的蓝图调用函数仍在开发中。核心目标是让开发者能够快速地在场景中叠加视觉调试元素，并支持自定义样式控制（如颜色、粗细）以及与 Visual Logger 的集成（录制时不绘制选项）。

## 使用场景

- 在游戏运行时需要实时查看碰撞、追踪、路径等调试可视化信息。
- 希望将调试绘制暴露给蓝图设计师，减少 C++ 依赖。
- 需要统一控制调试绘制的样式（颜色、粗细）和日志记录等级。
- 利用 Visual Logger 录制时，有选择地屏蔽场景中的调试绘制。

## 蓝图用法

因插件处于早期版本，当前头文件中仅公开了以下两个类型，尚未暴露可直接调用的蓝图函数节点。以下类型可作为参数用于未来或自定义的调试绘制节点。

| 类型 | 说明 | 所在模块 |
|---|---|---|
| `EDrawDebugLogVerbosity` | 调试绘制日志输出等级（Fatal / Error / Warning / Display / Log / Verbose / VeryVerbose） | DrawDebugLibrary |
| `FDrawDebugPointStyle` | 点绘制样式：粗细（0 表示像素点）和颜色（带 Alpha） | DrawDebugLibrary |

实际蓝图绘制节点（如 `DrawDebugLine`、`DrawDebugBox` 等）预期将在后续版本中添加。当前建议结合引擎原生的 `DrawDebugFunctions`（`Kismet System` 库）使用，或等待插件更新。

## C++ 用法

### 头文件引入

```cpp
#include "DrawDebugLibrary.h"
```

### 基本用法

```cpp
// 使用日志等级枚举
EDrawDebugLogVerbosity Verbosity = EDrawDebugLogVerbosity::Warning;

// 使用点样式结构体
FDrawDebugPointStyle PointStyle;
PointStyle.Thickness = 2.0f;
PointStyle.Color = FLinearColor::Red;
```

### 模块初始化和访问

插件模块类 `FDrawDebugLibraryModule` 继承自 `IModuleInterface`，可在模块加载时执行初始化逻辑。一般无需手动调用，但可通过 `FModuleManager::LoadModuleChecked<FDrawDebugLibraryModule>("DrawDebugLibrary")` 确保模块已加载。

## Demo 示例

鉴于当前插件仅公开了数据类型，暂无完整可编译的蓝图或 C++ 示例。以下是一个最小化 C++ 使用方法：

```cpp
// DrawDebugLibraryDemo.h
#pragma once
#include "CoreMinimal.h"
#include "DrawDebugLibrary.h"

class FDLLibDemo
{
public:
    static void DemoUsage()
    {
        EDrawDebugLogVerbosity LogLevel = EDrawDebugLogVerbosity::Verbose;
        FDrawDebugPointStyle Style;
        Style.Thickness = 0.0f;
        Style.Color = FLinearColor(1.0f, 0.0f, 0.0f, 0.5f);
        // 未来可使用Style进行点绘制
    }
};
```

## 模块依赖

该插件为纯运行时模块，不引入特殊的外部依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Core/Engine 等 |

（注：实际 Build.cs 中可能引用了 `Engine`、`Core` 等基础模块，按省略规则不列出。）

## 维护状态

### 近期更新

- 2025-09-23 `eaf93ed5` DrawDebugLibrary: Added ability to change line style
- 2025-09-23 `44d73218` [Backout] - CL45872704
- 2025-09-23 `9c26c083` DrawDebugLibrary: Added ability to change line style
- 2025-09-11 `fc9cea22` DrawDebugLibrary: Added option for not drawing to the scene during recording
- 2025-09-09 `5a7a6ce9` Fixed normalization issue in DrawDebugLibrary

### 维护评价

该插件创建于 2025-09-09，属于非常新的实验性插件。最近一个月内（至 2025-09-23）有多次功能性更新（线条样式、录制选项），修复了归一化问题，表明目前处于活跃开发阶段。但由于版本号为 0.1 且 `IsExperimentalVersion=true`，API 可能不稳定且功能不完整。推荐尝鲜使用，但应谨慎依赖，并关注后续迭代。尚未发现已知限制或废弃风险。

## 相关链接

- [源码（仓库根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DrawDebugLibrary)
- [官方文档] 无（当前无 DocsURL）
- [测试用例] 暂无公开测试用例