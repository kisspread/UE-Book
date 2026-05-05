# MetaHuman Animation Tools

> Tooling for working with MetaHuman Animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画数据资产） |
| 模块 | `MetaHumanAnimationSerialization` (Runtime), `MetaHumanAnimationSerializationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-02-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimationTools) | |

## 用途

MetaHuman Animation Tools 是 Epic 为 MetaHuman 角色动画工作流提供的序列化工具集。该插件解决的核心问题是：MetaHuman 角色的面部动画数据（通常来自 MetaHuman Animator 或其他面部捕捉流程）需要在引擎中进行高效的序列化、反序列化和编辑处理。

插件分为两个模块：
- **MetaHumanAnimationSerialization**（Runtime）：提供动画数据的运行时序列化/反序列化能力，确保打包后的项目也能正确加载 MetaHuman 动画数据
- **MetaHumanAnimationSerializationEditor**（Editor）：提供编辑器内的动画数据导入、预览和编辑工具

该插件默认隐藏且未启用，表明它可能是 MetaHuman 工具链的内部依赖组件，通常由其他 MetaHuman 工具（如 MetaHuman Animator）自动引用。

## 使用场景

- 你使用 MetaHuman Animator 捕捉面部动画 → 需要此插件来序列化动画数据到资产中
- 你在编辑器中导入和管理 MetaHuman 面部动画资产 → 使用 Editor 模块提供的工具
- 你在打包项目中播放 MetaHuman 面部动画 → Runtime 模块确保数据正确加载
- 你正在构建自定义的 MetaHuman 动画管线 → 可以基于此插件的序列化格式扩展

## 蓝图用法

> ⚠️ 该插件源文件数量较少（5个），且主要聚焦于序列化底层逻辑，蓝图暴露的接口可能有限。以下为基于模块结构推断的可能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 待源码分析确认 | 序列化/反序列化相关函数 | 待确认 |

### 使用示例（蓝图描述）

该插件主要提供底层序列化支持，通常不直接在蓝图中使用。动画数据的加载和播放由 MetaHuman 角色蓝图和动画蓝图自动处理。

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "MetaHumanAnimationSerialization.h"

// Editor 模块（仅在编辑器环境下）
#include "MetaHumanAnimationSerializationEditor.h"
```

### 基本用法

```cpp
// 基于模块结构推断的典型用法
// 实际 API 需参考源码确认

// 在运行时加载 MetaHuman 动画数据
// MetaHumanAnimationSerialization 模块提供序列化支持

// 在编辑器中处理动画数据导入
// MetaHumanAnimationSerializationEditor 模块提供编辑器工具
```

### 进阶用法

该插件通常作为 MetaHuman 工具链的底层依赖，高级用法涉及自定义动画管线集成。具体 API 请参考源码中的 Public 头文件。

## Demo 示例

```cpp
// MyMetaHumanAnimProcessor.h
#pragma once

#include "CoreMinimal.h"

// 引入 MetaHuman Animation Serialization 模块
// #include "MetaHumanAnimationSerialization/SomeHeader.h"

class FMyMetaHumanAnimProcessor
{
public:
    // 处理 MetaHuman 动画数据的示例框架
    void ProcessAnimationData();
};
```

```cpp
// MyMetaHumanAnimProcessor.cpp
#include "MyMetaHumanAnimProcessor.h"

void FMyMetaHumanAnimProcessor::ProcessAnimationData()
{
    // 使用 MetaHumanAnimationSerialization 模块
    // 进行动画数据的序列化/反序列化操作
    // 具体 API 请参考插件源码
}
```

## 模块依赖

> ⚠️ 由于未提供 Build.cs 的详细依赖信息，以下为基于 MetaHuman 生态系统的典型依赖推断。

| 模块 | 用途 |
|---|---|
| `MetaHumanSDK` | MetaHuman 核心 SDK，提供基础数据类型 |
| `MetaHumanIdentity` | MetaHuman 身份资产，关联角色与动画数据 |

> 实际依赖请参考各模块的 `.Build.cs` 文件确认。

## 维护状态

### 近期更新

- 2026-02-03 `f39fc2f9` Correct filename misspelling
- 2026-02-02 `b1aae96f` Add new plugin to efficiently serialize facial animation curve data

> ⚠️ 该插件创建时间较新（2026-02-02），git 历史记录有限。

### 维护评价

- **创建时间**：2026-02-02，非常新的插件
- **维护状态**：🆕 新创建，处于早期开发阶段
- **活跃度**：作为 MetaHuman 工具链的一部分，预计会随 MetaHuman 产品线持续更新
- **已知限制**：
  - 默认未启用且隐藏，表明可能尚未完全稳定
  - 源文件数量少（5个），功能可能仍在扩展中
- **推荐程度**：如果你使用 MetaHuman Animator 工作流，此插件是必要的底层依赖。对于自定义动画管线，建议关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimationTools)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-in-unreal-engine/)
- [MetaHuman Animator 文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/)