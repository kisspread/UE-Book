# Hierarchy Table Animation

> Animation-specific type definitions for Hierarchy Tables

| 属性 | 值 |
|---|---|
| 中文名 | 层级表动画 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义、编辑器工具） |
| 模块 | `HierarchyTableAnimationRuntime` (Runtime), `HierarchyTableAnimationEditor` (Editor), `HierarchyTableAnimationUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation) | |

## 用途

HierarchyTableAnimation 是通用 HierarchyTable 插件的动画专用扩展层。它解决的核心问题是：如何让骨骼层级结构与 Blend Profile（混合配置文件）建立关联，并提供一套完整的资产创建、编辑和管理流程。

具体来说，该插件实现了：

1. **独立的 Blend Profile 资产类型**（`UBlendProfileStandalone`）：脱离 AnimSequence 之外，独立管理混合配置文件，支持基于骨骼层级自动生成配置结构
2. **骨骼层级表类型处理器**：为 HierarchyTable 框架提供 Skeleton 专用的表类型实现，支持添加曲线（Curve）和属性（Attribute）到层级中
3. **Mask Profile 列**：在层级表中增加"遮罩"列，允许对每个节点进行遮罩控制
4. **Blend Profile 编辑器**：专用的资产编辑器，集成 HierarchyTable 视图进行可视化编辑

该插件是 HierarchyTable 框架在动画领域的具体应用，由最初名为 `HierarchyTableBuiltin` 的插件重命名而来（见首个 commit）。

## 使用场景

- 你需要创建独立于动画序列的 Blend Profile 资产，用于控制骨骼各部位的混合权重
- 你需要基于骨架（Skeleton）的骨骼层级结构，以可视化方式编辑混合配置
- 你需要在 HierarchyTable 中使用 Mask 列，对骨骼层级的每个节点进行遮罩控制
- 你正在开发动画系统，需要将通用的层级表框架应用于骨骼动画工作流
- 你需要将 Blend Profile 注册为资产，使其可在内容浏览器中创建、管理和复用

## 蓝图用法

该插件主要为编辑器扩展和资产工作流服务，公开的蓝图 API 较少。核心功能通过编辑器 UI 和资产工厂实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConstructBlendProfile` | 从自定义数据构建 Blend Profile | `UBlendProfileStandaloneProvider` |
| `Initialize` | 初始化 Blend Profile Provider | `UBlendProfileStandaloneProvider` |

### 使用示例（蓝图描述）

该插件的使用主要通过编辑器 UI 完成：

1. 在内容浏览器中右键 → Animation → Blend Profile Standalone 创建新资产
2. 资产创建向导会要求选择 Blend Profile 类型，并自动根据 Skeleton 构建层级结构
3. 在 Blend Profile 编辑器中，通过 HierarchyTable 视图对每个骨骼节点设置混合权重/遮罩值
4. 在动画蓝图或其他动画工具中引用该 Blend Profile 资产

## C++ 用法

### 头文件引入

```cpp
#include "HierarchyTableAnimationRuntimeModule.h"

// Editor 模块
#include "HierarchyTableAnimationEditorModule.h"

// Blend Profile 相关
#include "BlendProfileStandalone.h"
#include "BlendProfileStandaloneFactory.h"

// Hierarchy Table 类型处理
#include "SkeletonHierarchyTableTypeHandler.h"
```

### 基本用法

从源码中提取的表类型处理器用法：

```cpp
// 获取骨骼层级表类型处理器
// UHierarchyTable_TableTypeHandler_Skeleton 负责处理 Skeleton 类型的层级表
UHierarchyTable_TableTypeHandler_Skeleton* Handler = ...;

// 构建骨骼层级结构
Handler->ConstructHierarchy();

// 向层级中添加曲线（Curve）
// ParentIndex 指定父节点索引，Identifier 为曲线名称
// 来源: Private/SkeletonHierarchyTableTypeHandler.h
void AddCurve(const int32 ParentIndex, const FName Identifier) const;

// 向层级中添加属性（Attribute）
void AddAttribute(const int32 ParentIndex, const FName Identifier) const;
```

### 进阶用法

自定义 Blend Profile 工厂配置流程：

```cpp
// 创建独立 Blend Profile 资产
// UBlendProfileStandaloneFactory 负责资产创建向导
UBlendProfileStandaloneFactory* Factory = ...;

// 步骤1: 配置 Blend Profile 类型
// 弹出 UI 让用户选择 EBlendProfileStandaloneType
bool bTypeConfigured = Factory->ConfigureBlendProfileType();

// 步骤2: 配置层级结构
// 根据选择的类型和关联的 Skeleton 构建层级
bool bHierarchyConfigured = Factory->ConfigureBlendProfileHierarchy();

// 步骤3: 执行创建
// 来源: Private/BlendProfileStandaloneFactory.h
UObject* NewProfile = Factory->FactoryCreateNew(
    UBlendProfileStandalone::StaticClass(),
    InParent, Name, Flags, Context, Warn);
```

Provider 模式用于从外部数据构建 Blend Profile：

```cpp
// UBlendProfileStandaloneProvider 实现了 IBlendProfileProviderInterface
// 来源: Private/BlendProfileStandaloneProvider.h
UBlendProfileStandaloneProvider* Provider = NewObject<UBlendProfileStandaloneProvider>();

// 初始化，关联到特定的 BlendProfileStandalone 资产
Provider->Initialize(BlendProfileAsset);

// 构建对应的 BlendProfile（用于动画系统实际使用）
UBlendProfile* OutProfile = ...;
Provider->ConstructBlendProfile(OutProfile);
```

## Demo 示例

### 骨骼层级表类型处理器扩展

```cpp
// MySkeletonTableTypeExtension.h
#pragma once

#include "CoreMinimal.h"
#include "SkeletonHierarchyTableTypeHandler.h"

// 继承骨骼表类型处理器，添加自定义行为
class FMySkeletonTableTypeExtension
{
public:
    // 示例：在特定骨骼下添加自定义曲线
    static void AddCustomCurveToHierarchy(
        UHierarchyTable_TableTypeHandler_Skeleton* Handler,
        const int32 ParentBoneIndex,
        const FName CurveName)
    {
        // 通过 Handler 的 AddCurve 方法添加
        // Handler->AddCurve(ParentBoneIndex, CurveName);
    }
    
    // 示例：检查节点是否可以被重命名
    static bool CanModifyEntry(
        UHierarchyTable_TableTypeHandler_Skeleton* Handler,
        const int32 EntryIndex)
    {
        // 检查重命名权限
        // return Handler->CanRenameEntry(EntryIndex);
        return false;
    }
};
```

```cpp
// MyBlendProfileAssetCreator.cpp
#include "MyBlendProfileAssetCreator.h"
#include "BlendProfileStandalone.h"
#include "BlendProfileStandaloneFactory.h"
#include "HierarchyTable_TableTypeHandler.h"

UBlendProfileStandalone* UMyBlendProfileAssetCreator::CreateBlendProfile(
    UObject* InOuter,
    const FName InName,
    USkeleton* TargetSkeleton)
{
    // 1. 创建工厂实例
    UBlendProfileStandaloneFactory* Factory = NewObject<UBlendProfileStandaloneFactory>();
    
    // 2. 配置表元数据（关联 Skeleton）
    FInstancedStruct TableMetadata;
    // TableMetadata 初始化为 Skeleton 类型...
    
    // 3. 使用工厂创建资产
    UObject* NewAsset = Factory->FactoryCreateNew(
        UBlendProfileStandalone::StaticClass(),
        InOuter,
        InName,
        RF_Public | RF_Standalone,
        nullptr,
        GWarn);
    
    return Cast<UBlendProfileStandalone>(NewAsset);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HierarchyTable` | 核心层级表框架，提供 UHierarchyTable、IHierarchyTable 等基础设施 |
| `BlendProfile` | Blend Profile 基础类型和接口（IBlendProfileProviderInterface） |

> 无其他特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `711fdc2f` | Add root space support to profile blend | 为 Profile Blend 添加根空间支持 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新 UAF 混合配置文件 |
| 2025-10-20 | `beb220c7` | Fix loaded blend profile assets not updating the hierarchy when its skeleton's hierarchy has changed | 修复骨架层级变更后已加载的 Blend Profile 不更新层级的问题 |
| 2025-10-09 | `71d54d3d` | Fix profile blend node crash due to cached data not being generated in some cases | 修复某些情况下缓存数据未生成导致的 Profile Blend 节点崩溃 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将 Base 配置文件重命名为 Default 配置文件 |

### 维护评价

- **年龄**：创建于 2024 年 11 月，至今约 1 年，属于较新的插件
- **活跃度**：持续活跃维护，最近一次更新在 2026 年 5 月，包含功能增强（根空间支持）
- **稳定性**：近期有多次 Bug 修复（层级更新、崩溃修复），表明插件仍在迭代完善中
- **实验状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动启用
- **推荐度**：适合对 Blend Profile 有高级需求的动画开发者，但由于处于实验阶段，生产环境使用需谨慎

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation)
- 官方文档：暂无（DocsURL 为空）