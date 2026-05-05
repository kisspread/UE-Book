# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码库） |
| 模块 | `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-01-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHumanCoreTech 是 MetaHuman Creator 和 MetaHuman Animator 插件的底层技术库。它并非一个面向最终用户的独立功能插件，而是为上述两个高级插件提供核心算法、数据结构和处理流程的基石。其主要解决数字人（MetaHuman）创建、动画驱动以及相关数据处理中的底层技术问题，例如面部捕捉数据的解析、图像处理、以及构建可扩展的处理流水线。

## 使用场景

- 你正在开发或扩展 **MetaHuman Creator** 的功能，需要访问其底层的资产处理、网格生成或材质逻辑。
- 你正在开发或扩展 **MetaHuman Animator** 的功能，需要处理面部捕捉数据流、进行图像分析或驱动面部动画。
- 你需要构建一个**自定义的面部动画处理流水线**，并希望复用或集成 MetaHuman 的核心算法和数据结构。
- 你正在研究 MetaHuman 的技术实现，需要理解其模块化架构和核心数据类型。

## 蓝图用法

作为底层技术库，此插件主要通过 C++ API 提供功能。其蓝图接口通常由上层插件（如 MetaHuman Creator/Animator）封装暴露。直接使用此插件的蓝图节点较少，主要集中在数据查看和流程控制方面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateImageViewer` | 创建一个用于查看图像数据的查看器实例。 | `UMetaHumanImageViewerSubsystem` |
| `ProcessCaptureData` | 对输入的捕捉数据执行处理流程。 | `UMetaHumanPipelineSubsystem` |

*详细的蓝图 API 请参考各子模块文档。*

## C++ 用法

此插件的 C++ 用法是其主要使用方式。开发者需要链接相应的模块，并使用其提供的类和函数来构建功能。

### 头文件引入

```cpp
// 根据需要引入具体模块的头文件
#include "MetaHumanCaptureData.h"
#include "MetaHumanPipelineCore.h"
```

### 基本用法

使用 `MetaHumanPipelineCore` 模块定义和执行一个简单的处理节点。

```cpp
// 来源：MetaHumanPipelineCore 模块文档示例
#include "MetaHumanPipeline.h"

// 定义一个自定义处理节点
class FMyCustomNode : public FMetaHumanPipelineNode
{
public:
    virtual void Process(const FMetaHumanPipelineData& InData, FMetaHumanPipelineData& OutData) override
    {
        // 实现你的处理逻辑
    }
};

// 在某个管理器中注册并运行
FMetaHumanPipeline Pipeline;
Pipeline.AddNode<FMyCustomNode>();
Pipeline.Execute(InputData);
```

*更详细的 C++ API 和用法，请查阅各子模块文档。*

## 模块列表

本插件由以下五个核心模块组成，共同构成了 MetaHuman 的技术底座：

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| **MetaHumanCaptureData** | Runtime | 负责定义和管理面部捕捉相关的数据类型和资产。 |
| **MetaHumanCoreTech** | Runtime | 包含 MetaHuman 的核心算法和通用技术实现。 |
| **MetaHumanCoreTechLib** | Runtime | 底层技术库，提供基础工具和与外部系统（如在线子系统）的集成。 |
| **MetaHumanImageViewer** | Runtime | 提供图像数据的查看、调试和可视化功能。 |
| **MetaHumanPipelineCore** | Runtime | 定义并实现了可扩展的处理流水线框架，用于编排复杂的数据处理任务。 |

*每个模块的详细 API、类说明和用法示例，请参见对应的模块文档。*

## 模块依赖

使用此插件时，你的项目模块需要依赖以下**独特**的模块（除标准 Core/Engine 等之外）：

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewer` | 用于图像数据查看功能。 |
| `DirectoryWatcher` | 用于监控文件系统目录变化（如资产更新）。 |
| `UnrealEd` | 编辑器功能支持（部分模块）。 |
| `OnlineSubsystem` | 用于在线服务集成（如账户、云处理）。 |
| `OpenCVHelper` | 提供 OpenCV 库的辅助封装。 |
| `OpenCV` | 计算机视觉库，用于图像分析和处理。 |

## 维护状态

### 近期更新

由于此插件创建时间非常近（2025年1月），且属于 MetaHuman 核心技术栈，预计会随着 MetaHuman Creator/Animator 的更新而持续维护。具体的近期 commit 信息需要从主仓库的 `Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/` 路径获取。

### 维护评价

- **创建时间**：非常新（约 0 年），是 MetaHuman 技术栈的最新底层重构或模块化成果。
- **维护状态**：**活跃维护中**。作为 Epic 官方 MetaHuman 工具链的核心部分，其维护与 MetaHuman Creator 和 Animator 的开发周期紧密绑定，预计会持续获得更新和 bug 修复。
- **已知限制**：这是一个**底层技术库**，默认未启用（`EnabledByDefault: false`）。它通常由上层插件自动依赖和启用，不建议普通用户直接在项目中手动启用和使用，除非有明确的底层开发需求。
- **推荐使用**：对于**普通用户**，不推荐直接使用此插件，请使用 MetaHuman Creator 或 MetaHuman Animator。对于**高级开发者和工具开发者**，如果你需要深度定制或扩展 MetaHuman 功能链，此插件是必须研究和依赖的基础。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- [官方文档]() (暂无直接链接，请参考 MetaHuman Creator/Animator 文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Tests) (如果存在)