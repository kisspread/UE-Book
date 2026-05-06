# Nanite Displaced Mesh

> Asset and component types that provide a basic pre-displacement pipeline for Nanite meshes

| 属性 | 值 |
|---|---|
| 中文名 | Nanite 位移网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、命令、工厂） |
| 模块 | `NaniteDisplacedMesh` (Runtime), `NaniteDisplacedMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteDisplacedMesh) | |

## 用途

Nanite 位移网格插件提供了一套资产和组件类型，用于为 Nanite 网格实现基本的预位移管线。它允许开发者通过位移贴图生成高细节的网格变体，同时保持 Nanite 的渲染性能优势。

该插件解决的问题是：在 Nanite 系统中，网格的几何复杂性由系统自动处理，但传统的位移技术（如顶点位移）需要预处理。此插件通过**预位移**方式，在导入或生成时根据地形的位移参数创建离散的网格实例，并支持链接到原始网格资产，从而实现类似“置换贴图”的效果，但完全在 Nanite 框架下工作。

## 使用场景

- **程序化地形细节**：你需要一个低面基准网格，通过位移贴图生成不同高度/形状的 Nanite 网格实例（如岩石、地面突起）。
- **动态网格修改**：在编辑器中为已有 Nanite 网格添加位移效果，并希望效果保留为独立的资产。
- **批量生成与更新**：通过命令或脚本在多个关卡中自动生成或更新位移网格资产，保持与源网格的同步。

## 蓝图用法

此插件的核心功能主要在 C++ 层暴露，蓝图可用的 API 有限。通过 `UGeneratedNaniteDisplacedMeshEditorSubsystem` 可以为蓝图提供底层回调支持，但无直接的蓝图节点。建议通过 C++ 或控制台命令 `GenerateNaniteDisplacedMeshCommandlet` 使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Link Displaced Mesh Asset` | 链接或创建位移网格资产（已废弃，推荐使用 C++ 新重载） | `NaniteDisplacedMeshFactory.h` |
| `Generate Displaced Mesh Asset Name` | 根据参数生成位移网格资产的名称 | `NaniteDisplacedMeshFactory.h` |
| `Get Aggregated Id` | 获取位移网格参数的聚合 ID（用于去重） | `NaniteDisplacedMeshFactory.h` |

> 以上函数为 `NANITEDISPLACEDMESHEDITOR_API` 导出，蓝图不可直接调用，但可通过自定义蓝图库封装。

## C++ 用法

### 头文件引入

```cpp
#include "NaniteDisplacedMesh.h"           // Runtime 核心类型
#include "NaniteDisplacedMeshFactory.h"     // 工厂与链接函数
#include "GeneratedNaniteDisplacedMeshEditorSubsystem.h" // 自动依赖更新
```

### 基本用法

#### 创建或链接位移网格资产

```cpp
// source: Engine/Plugins/Experimental/NaniteDisplacedMesh/Source/NaniteDisplacedMeshEditor/Private/NaniteDisplacedMeshFactory.cpp

UNaniteDisplacedMesh* ExistingMesh = ...; // 如果已有
FValidatedNaniteDisplacedMeshParams Params;
// 填充参数...

FNaniteDisplacedMeshLinkParameters LinkParams;
LinkParams.DisplacedMeshFolder = TEXT("/Game/MyDisplacedMeshes");
LinkParams.LinkDisplacedMeshAssetSetting = ELinkDisplacedMeshAssetSetting::LinkAgainstPersistentAsset;

bool bCreated = false;
LinkParams.bOutCreatedNewMesh = &bCreated;
UNaniteDisplacedMesh* Result = LinkDisplacedMeshAsset(ExistingMesh, MoveTemp(Params), LinkParams);
// Result 为新创建或已有的网格资产
```

#### 使用命令重新生成所有链接的网格

```cpp
// source: Engine/Plugins/Experimental/NaniteDisplacedMesh/Source/NaniteDisplacedMeshEditor/Private/GenerateNaniteDisplacedMeshCommandlet.cpp

// 在控制台执行：
// UE4Editor-Cmd.exe "path/to/project.uproject" -run=GenerateNaniteDisplacedMesh -PackageFolders="/Game/MyMaps" -NamePrefix="DM_"
// 该命令会遍历指定文件夹中的关卡，为每个链接的位移网格重新生成资产。
```

#### 注册自定义依赖更新回调

```cpp
// 在 EditorSubsystem 初始化时
UGeneratedNaniteDisplacedMeshEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UGeneratedNaniteDisplacedMeshEditorSubsystem>();
if (Subsystem)
{
    UGeneratedNaniteDisplacedMeshEditorSubsystem::FActorClassHandler Handler;
    Handler.Callback = [](AActor* Actor, UObject* Asset, FPropertyChangedEvent& Event)
    {
        // 当依赖资产变化时，更新 Actor 引用的网格
    };
    // 监听某类 Actor 的依赖变化
    Subsystem->RegisterClassHandler(AMyCustomActor::StaticClass(), MoveTemp(Handler));
}
```

### 进阶用法

#### 使用细节定制面板

`FNaniteDisplacedMeshDetails` 提供自定义细节面板，在选中一个 `UNaniteDisplacedMesh` 资产时，会显示“Apply”按钮以应用参数。可通过 `FReply ApplyNaniteDisplacedMeshParams()` 触发重新生成。

#### 集成到资产编辑器

`FAssetTypeActions_NaniteDisplacedMesh` 注册了资产动作，支持右键菜单中打开编辑器、获取颜色等。可通过继承 `FAssetTypeActions_Base` 扩展现有行为。

## Demo 示例

以下是一个最小示例，演示在编辑器模块中如何通过 `LinkDisplacedMeshAsset` 动态创建位移网格。

**MyMeshGenerator.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "NaniteDisplacedMeshFactory.h"

class FMyMeshGenerator
{
public:
    static UNaniteDisplacedMesh* GenerateDisplacedMesh(
        const FString& InPackagePath,
        const FValidatedNaniteDisplacedMeshParams& InParams)
    {
        FNaniteDisplacedMeshLinkParameters LinkParams;
        LinkParams.DisplacedMeshFolder = InPackagePath;
        LinkParams.LinkDisplacedMeshAssetSetting = ELinkDisplacedMeshAssetSetting::LinkAgainstPersistentAsset;
        bool bCreated = false;
        LinkParams.bOutCreatedNewMesh = &bCreated;
        return LinkDisplacedMeshAsset(nullptr, FValidatedNaniteDisplacedMeshParams(InParams), LinkParams);
    }
};
```

**MyMeshGenerator.cpp**

```cpp
#include "MyMeshGenerator.h"

// 调用示例（如在命令let中）：
void GenerateExample()
{
    FValidatedNaniteDisplacedMeshParams Params;
    // 设置位移参数...
    // Params.SourceMesh = ...;
    // Params.DisplacementTexture = ...;
    // ...
    
    UNaniteDisplacedMesh* NewMesh = FMyMeshGenerator::GenerateDisplacedMesh(
        TEXT("/Game/GeneratedMeshes"), Params);
    if (NewMesh)
    {
        UE_LOG(LogTemp, Log, TEXT("Created displaced mesh: %s"), *NewMesh->GetPathName());
    }
}
```

## 模块依赖

需要将插件添加到项目的 `.uproject` 或 `Plugins` 目录，并手动启用（实验性，需添加 `"Enabled": true`）。

**依赖（仅列出非标准模块）：**

| 模块 | 用途 |
|---|---|
| `NaniteDisplacedMesh` | Runtime 核心类型与网格数据 |
| `AssetTools` | 资产类型注册与菜单 |
| `UnrealEd` | 编辑器子系统、命令let、细节定制 |

> 其余通用依赖（Core, Engine, Slate 等）已省略。

## 维护状态

### 近期更新

- 2025-09-29 `32dcdf1c` — Cooker: SkipOnlyEditorOnly: Nanite: Mark that the NaniteDisplacedMesh package loads are editor-only
- 2025-09-12 `f89d77ef` — Additional non-unity fixes from removing GCObject.h from StrongObjectPtr.h
- 2025-08-22 `d82d12d8` — Enable Geometry::TAdaptiveTessellator for Nanite tessellation
- 2025-08-07 `45c08907` — [Backout] - CL44647866
- 2025-08-07 `f7c6b9f6` — Enable Geometry::TAdaptiveTessellator for Nanite tessellation

### 维护评价

该插件仍处于**实验性阶段**（`IsBetaVersion=true`），但近期（2025年8-9月）有多次功能更新和修复，包括启用自适应细分、优化编辑器加载等，表明团队仍在积极迭代。由于是预位移管线，较为前沿，API 可能在未来版本中变化或废弃（如 `OnLinkDisplacedMesh` 已废弃）。对于需要 Nanite 位移效果的正式项目，建议谨慎使用并做好兼容性准备。

## 相关链接

- [源码 (主线)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteDisplacedMesh)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteDisplacedMesh/Tests) （如存在）
- UDN 讨论：Nanite Displaced Mesh 使用指南（内部 Epic 文档）