# Actor Layer Utilities

> Utilites for interacting with actor layers from blueprints

| 属性 | 值 |
|---|---|
| 中文名 | Actor 图层工具 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorLayerUtilities` (Runtime), `ActorLayerUtilitiesEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ActorLayerUtilities) | |

## 用途

UE 编辑器中的 **Actor Layers（图层）** 是一种将关卡中的 Actor 按图层分组管理的机制，类似于 Photoshop 的图层概念。开发者可以在编辑器中创建不同图层，将 Actor 分配到特定图层，然后按图层整体控制可见性、选择范围等。

本插件的核心作用是**将 Actor 图层的交互能力暴露给蓝图**，使得运行时和编辑器蓝图脚本都能方便地读取和操作 Actor 图层。编辑器模块（`ActorLayerUtilitiesEditor`）还提供了自定义属性面板 UI，支持拖拽分配图层等便捷操作。

## 使用场景

- 你在编辑器中使用 Actor Layers 组织关卡内容，需要在蓝图中按图层筛选 Actor → 用本插件
- 你需要在蓝图脚本中动态获取特定图层中的所有 Actor → 用本插件
- 你需要在编辑器的属性面板中为 Actor Layer 属性提供更好的编辑体验（拖拽分配、图层浏览器）→ 编辑器模块自动提供

## 蓝图用法

本插件将 Actor Layer 相关结构体和函数暴露给蓝图，使得蓝图能够与编辑器图层系统交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| Actor Layer 相关结构体 | 用于表示和传递图层信息的蓝图可用结构体 | `FActorLayer` 等 |

> **注意**：由于未提供 Runtime 模块的完整头文件，具体蓝图节点请在编辑器中搜索 `Actor Layer` 关键词查看所有可用节点。

### 使用示例（蓝图描述）

1. **按图层获取 Actor 列表**：使用插件提供的蓝图函数，传入目标图层名称，获取该图层下的所有 Actor 引用
2. **设置 Actor 图层**：将指定 Actor 添加到目标图层，或从图层中移除

## C++ 用法

### 头文件引入

```cpp
#include "ActorLayerUtilities.h"  // Runtime 模块
```

### 基本用法

```cpp
// 引入 Actor Layer 工具模块头文件
#include "ActorLayerUtilities.h"

// 使用 FActorLayer 结构体在 C++ 中标识图层
FActorLayer MyLayer;
MyLayer.Name = FName("MyLayerName");

// 通过插件提供的工具函数与图层系统交互
// （具体函数签名请参考 Runtime 模块源码）
```

## 模块依赖

由于未提供完整的 `Build.cs` 源码，以下为基于插件功能推断的依赖关系：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | — |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies. | 优化头文件依赖，移除不必要的私有模块引用 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 插件目录通用更新 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 插件目录通用更新 |
| 2022-10-26 | `b5b86c79` | This change is a strategical submit for a coming change that removes lots of includes in headers tha... | 策略性提交，为后续清理头文件包含做准备 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件内置链接为安全协议（HTTPS） |

### 维护评价

- **创建时间**：2020 年 10 月（约 5 年），随 UE5 早期分支从 UE4 迁移而来
- **最近更新**：最近一次实质性更新在 2023 年 5 月，此后无新改动
- **更新内容**：近两次更新均为依赖优化和通用头文件清理，无新功能添加
- **维护状态**：**维护不活跃** — 超过 2 年无实质性功能更新
- **代码规模**：仅 5 个源文件，功能单一且稳定，不活跃维护属于正常现象

**综合评价**：本插件功能简单且成熟，属于工具型小插件。由于图层系统本身已是编辑器的核心功能，插件仅提供蓝图桥梁，无需频繁更新。**推荐使用**，无需担心维护问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ActorLayerUtilities)