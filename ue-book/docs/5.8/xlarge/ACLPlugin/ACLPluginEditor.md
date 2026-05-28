# Animation Compression Library

> Use the Animation Compression Library (ACL) to compress AnimSequences.

| 属性 | 值 |
|---|---|
| 中文名 | 动画压缩库 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（压缩编解码器资产） |
| 模块 | `ACLPlugin` (Runtime), `ACLPluginEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ACLPlugin) | |

## 用途

ACLPlugin 是 Unreal Engine 内置的高性能动画压缩解决方案。它基于开源的 [Animation Compression Library (ACL)](https://github.com/nicholasfrechette/acl) 库实现，主要目标是**在保持高视觉保真度的前提下，显著减小动画序列（AnimSequence）的内存占用和磁盘大小，并提升运行时解压缩性能**。

此插件解决了 UE 默认动画压缩方案（如 Key Reduction）在压缩率、解压速度和保真度之间难以取得最佳平衡的问题。ACL 通过更先进的压缩算法和数据格式，实现了更高的压缩比和更快的解压速度，对于需要存储和播放大量高质量动画的游戏项目（如开放世界、动作游戏）至关重要。它同时提供了运行时管理器（ACLDatabase）来优化动画数据的流式加载和解压。

## 使用场景

- **大型开放世界游戏**：拥有数千个动画片段，需要极致压缩以减少包体大小和内存占用。
- **动作密集型游戏**：需要频繁播放高精度动画，要求解压速度快，以避免 CPU 成为瓶颈。
- **跨平台项目**：ACL 支持广泛的平台，可为所有目标平台提供统一且优化的压缩。
- **资产管线优化**：项目需要自动化的、高保真的动画压缩流程，替代手动调整压缩参数。

## 蓝图用法

ACLPlugin 的核心运行时功能通过 `UAnimBoneCompressionCodec_ACL` 类暴露给蓝图和编辑器。编辑器模块 `ACLPluginEditor` 提供了数据库资产（`UAnimationCompressionLibraryDatabase`）的管理和构建功能。

### 核心节点

由于提供的源码主要为编辑器模块头文件，运行时蓝图节点需要在 `ACLPlugin` 模块中查找。以下为基于编辑器模块的核心资产操作节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenAssetEditor` | 打开 ACL 数据库资产编辑器 | `FAssetTypeActions_AnimationCompressionLibraryDatabase` |
| `ExecuteBuild` | 构建/更新 ACL 数据库资产 | `FAssetTypeActions_AnimationCompressionLibraryDatabase` |
| `GetSubMenus` | 获取资产在内容浏览器中的子菜单 | `FAssetTypeActions_AnimationCompressionLibraryDatabase` |

### 使用示例（蓝图描述）

1.  **配置压缩设置**：在项目设置或动画资产压缩设置中，选择 `AnimBoneCompressionCodec_ACL` 作为骨骼动画压缩编解码器。
2.  **创建数据库资产**：在内容浏览器中右键 -> 动画 -> ACL Database，创建 `UAnimationCompressionLibraryDatabase` 资产。
3.  **构建数据库**：打开创建的数据库资产，使用工具栏上的“Build”按钮（或在蓝图中调用相关构建逻辑），该过程会收集相关的动画片段并优化其数据存储。
4.  **应用压缩**：批量或单个选择动画序列，在资产详情中选择之前配置的 ACL 压缩设置进行压缩。

## C++ 用法

### 头文件引入

```cpp
// 引入ACL插件运行时模块
#include "ACLPlugin.h"

// 引入ACL数据库相关类型
#include "AnimationCompressionLibraryDatabase.h"
```

### 基本用法

在 C++ 中配置动画压缩设置，通常是在加载或创建动画资产时。

```cpp
// 假设你已经获取了一个 UAnimSequence* AnimSequence
// 来源：基于 UAnimBoneCompressionCodec 的用法模式推断

// 1. 获取默认的ACL压缩编解码器
UAnimBoneCompressionSettings* ACLSettings = LoadObject<UAnimBoneCompressionSettings>(nullptr, TEXT("/ACLPlugin/DefaultACLSettings.DefaultACLSettings"));

// 2. 将ACL设置应用到动画序列
if (AnimSequence && ACLSettings)
{
    // 注意：实际操作可能是通过动画编辑器UI或自动化管线，以下为概念性代码
    AnimSequence->BoneCompressionSettings = ACLSettings;
    // 标记为需要重新压缩
    AnimSequence->MarkPackageDirty();
    // 通常会触发异步压缩任务
}
```

### 进阶用法

管理 ACL 数据库资产，用于运行时流式加载和优化。

```cpp
// 加载已创建的ACL数据库资产
// 来源：基于 FAssetTypeActions_AnimationCompressionLibraryDatabase::ExecuteBuild 推断

UAnimationCompressionLibraryDatabase* ACLDatabase = LoadObject<UAnimationCompressionLibraryDatabase>(nullptr, TEXT("/Game/Anim/ACLDatabase"));

if (ACLDatabase)
{
    // 触发数据库的构建/更新流程
    // 在编辑器工具中，这对应于点击 “Build” 按钮
    // 在运行时或自动化脚本中，需要调用相应的构建函数（可能由UACLDatabaseBuildCommandlet提供）
    
    // 获取数据库映射信息，用于动画播放时查找最优压缩数据
    const FACLDatabaseMapping& Mapping = ACLDatabase->GetDatabaseMapping();
    // Mapping 包含了动画片段ID到其压缩数据在数据库中偏移量的映射
}
```

## Demo 示例

以下示例展示了如何在 C++ 中创建一个自定义的动画压缩编解码器实例，并基于 ACL 进行简单配置。

**MyACLCompressionHelper.h**
```cpp
// MyACLCompressionHelper.h
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimBoneCompressionCodec.h"

class UMyACLCompressionHelper
{
public:
    /**
     * 获取一个使用ACL压缩的编解码器实例。
     * 在实际项目中，通常通过资产直接引用UAnimBoneCompressionCodec_ACL。
     * 此处演示创建过程。
     */
    static UAnimBoneCompressionCodec* GetOrCreateACLCodec();

private:
    static UAnimBoneCompressionCodec* CachedACLCodec;
};
```

**MyACLCompressionHelper.cpp**
```cpp
// MyACLCompressionHelper.cpp
#include "MyACLCompressionHelper.h"
#include "AnimBoneCompressionCodec_ACL.h" // ACL编解码器具体类头文件

UAnimBoneCompressionCodec* UMyACLCompressionHelper::CachedACLCodec = nullptr;

UAnimBoneCompressionCodec* UMyACLCompressionHelper::GetOrCreateACLCodec()
{
    if (!CachedACLCodec)
    {
        // 在内存中创建一个临时的ACL编解码器对象用于演示。
        // 在真实资产管线中，应使用 LoadObject 加载预配置好的压缩设置资产。
        CachedACLCodec = NewObject<UAnimBoneCompressionCodec_ACL>(GetTransientPackage(), NAME_None, RF_NoFlags);
        
        // 通常不需要在此处设置参数，参数由 UAnimBoneCompressionSettings 资产管理。
        // CachedACLCodec->SomeParameter = ...;
    }
    return CachedACLCodec;
}

// 使用示例（概念性）
void ExampleUsage()
{
    UAnimBoneCompressionCodec* ACLCodec = UMyACLCompressionHelper::GetOrCreateACLCodec();
    if (ACLCodec)
    {
        // 将此编解码器用于动画压缩流程...
        // 注意：直接使用 NewObject 创建的编解码器不会被资产系统管理，仅作演示。
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationDataController` | 编辑器动画数据操作核心，ACLPluginEditor 依赖它来编辑动画序列和数据库。 |
| `TraceLog` | 运行时性能跟踪日志，用于分析 ACL 压缩/解压缩的性能。 |
| `DesktopPlatform` | 桌面平台功能，用于可能的文件对话框操作（如 `UACLStatsDumpCommandlet`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏格式。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复一次错误的查找替换后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了变更列表 51314860 的改动。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复了因核心代理事件获取方式变更导致的注册缺失问题。 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 移除了大量不再需要的 PVS 静态分析抑制标记。 |

### 维护评价

ACLPlugin 是一个**活跃维护中**的核心动画功能插件。
- **创建时间**：约 3 年前（2023年）从 ACL 外部库集成到引擎插件目录。
- **更新频率**：近期（2026年）有多次更新，主要集中在**代码规范化**（迁移 `UE_LOG`）、**稳定性修复**（回退错误提交、修复代理注册）和**代码清理**（移除 PVS 抑制）。
- **维护状态**：虽然近期更新多为底层修复和清理，但结合其作为 Epic Games 官方支持的动画压缩方案的地位，可以判断其仍处于**积极维护**状态，以确保与引擎新版本的兼容性和稳定性。
- **推荐度**：**强烈推荐使用**。对于任何对动画内存和性能有要求的项目，ACLPlugin 都是比 UE 默认方案更优的选择。其压缩率、速度和质量均经过验证，并且有官方持续支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ACLPlugin)
- [官方文档](https://docs.unrealengine.com/)（无直接链接，请在官方文档站搜索 “Animation Compression Library” 或 “ACL”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Animation/ACLPlugin/Source/ACLPluginEditor/Classes/ACLStatsDumpCommandlet.h)（`UACLStatsDumpCommandlet` 可视为一种性能分析和验证工具）