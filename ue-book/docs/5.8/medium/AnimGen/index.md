# AnimGen

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、蓝图） |
| 模块 | `AnimGen` (Runtime), `AnimGenEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimGen) | |

## 用途

AnimGen 是一个实验性的动画生成插件，旨在通过程序化或编辑器工具的方式，辅助或自动化创建动画资产。它可能包含用于在编辑器中批量处理、生成或修改动画序列、动画蓝图或相关资产的功能，以提升动画制作流程的效率。

## 使用场景

- 你需要为大量相似角色或物体快速生成基础动画变体。
- 你希望在编辑器中通过规则或算法程序化生成动画序列，减少手动关键帧工作。
- 你需要一个集成的编辑器工具来管理、预览和批量操作动画生成任务。

## 蓝图用法

该插件主要提供编辑器工具和运行时子系统。蓝图中可能通过特定的子系统或工具类来触发动画生成流程。详细的蓝图节点和用法请参考各模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `生成动画序列` | 根据配置程序化生成一个动画序列资产 | `UAnimGenSubsystem` |

*（注：具体节点名称和类名需根据源码确认，此处为示例）*

## C++ 用法

该插件的核心逻辑通过 C++ 模块暴露，通常通过获取相应的子系统或管理器类来使用。

### 头文件引入

```cpp
#include "AnimGen.h"
```

### 基本用法

```cpp
// 获取动画生成子系统
UAnimGenSubsystem* AnimGenSubsystem = GEditor->GetEditorSubsystem<UAnimGenSubsystem>();
if (AnimGenSubsystem)
{
    // 配置生成参数
    FAnimGenParams Params;
    // ... 设置参数
    
    // 触发动画生成
    AnimGenSubsystem->GenerateAnimation(Params);
}
```

*（注：以上为基于模块结构的推测示例，具体 API 请参考 `AnimGen` 模块文档）*

## Demo 示例

一个最小示例，展示如何在编辑器工具中调用 AnimGen 的核心功能。

**AnimGenDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FAnimGenDemo
{
public:
    static void RunDemo();
};
```

**AnimGenDemo.cpp**
```cpp
#include "AnimGenDemo.h"
#include "AnimGenSubsystem.h"

void FAnimGenDemo::RunDemo()
{
    UAnimGenSubsystem* Subsystem = GEditor->GetEditorSubsystem<UAnimGenSubsystem>();
    if (Subsystem)
    {
        UE_LOG(LogTemp, Log, TEXT("AnimGen Subsystem found. Ready to generate animations."));
        // 在此添加具体的生成调用
    }
}
```

## 模块依赖

使用此插件，你的项目模块可能需要依赖以下模块（具体取决于你使用的功能）：

| 模块 | 用途 |
|---|---|
| `AnimGen` | 核心运行时动画生成逻辑 |
| `AnimGraphRuntime` | 动画蓝图运行时支持 |
| `AnimationCore` | 动画核心数据结构和工具 |
| `AnimGraph` | 动画蓝图编辑器支持（若使用编辑器功能） |
| `BlueprintGraph` | 蓝图图表编辑器支持（若使用编辑器功能） |

## 维护状态

### 近期更新

*（由于插件为新创建，暂无历史提交记录）*

### 维护评价

- **创建时间**：2026年4月，是一个非常新的插件。
- **状态**：标记为**实验性** (`IsExperimentalVersion: true`) 且**默认未启用** (`EnabledByDefault: false`)，表明它仍处于早期开发或验证阶段。
- **维护活跃度**：作为新插件，预计会有活跃的初始开发。
- **推荐使用**：目前仅推荐用于实验、原型开发或学习目的。不建议在生产项目中依赖此插件，因为其 API 和功能可能在未来版本中发生重大变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimGen)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/AnimGen)（如果存在）