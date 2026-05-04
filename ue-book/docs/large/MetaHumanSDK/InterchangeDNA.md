# InterchangeDNA

> InterchangeDNA 是 MetaHumanSDK 的子模块，负责将 `.dna` 文件通过 Unreal 的 Interchange 框架翻译为 SkeletalMesh、MorphTarget 等资产。

## 用途

InterchangeDNA 模块是 MetaHuman DNA 格式与 UE5 Interchange 导入管线之间的桥梁。它实现了一个 `UInterchangeTranslatorBase` 子类（`UMetaHumanInterchangeDnaTranslator`），能够解析 RigLogic 的 `.dna` 二进制文件，提取网格拓扑、UV、法线、蒙皮权重、BlendShape（MorphTarget）以及骨骼层级，然后将这些数据转换为 Interchange 节点树，供下游 Pipeline 和 Factory 生成最终的 SkeletalMesh 资产。

模块同时提供 `FInterchangeDnaModule::ImportSync()` 便捷函数，可以在 C++ 中以同步方式一键导入 DNA 为 SkeletalMesh，内部会创建临时 DNA 文件并走完整的 Interchange 导入流程。

**核心问题**：MetaHuman 角色的面部数据以 DNA 格式存储（由 Meta Creator 导出），需要一个标准化的导入路径将其转化为引擎可用的 SkeletalMesh 资产。InterchangeDNA 就是这个路径的翻译层。

## 使用场景

- 你从 MetaHuman Creator 导出了 `.dna` 文件，需要在 UE 中导入为带 BlendShape 的面部 SkeletalMesh → 使用 InterchangeDNA 的翻译器
- 你在 C++ 代码中需要程序化地将 DNA 数据导入为 SkeletalMesh → 调用 `FInterchangeDnaModule::ImportSync()`
- 你需要为导入的 SkeletalMesh 附加 DNA AssetUserData（用于后续 RigLogic 驱动） → 调用 `FInterchangeDnaModule::SetSkelMeshDNAData()`

## 蓝图用法

本模块为 Editor 模块，主要面向 C++ 和编辑器导入流程，不暴露 BlueprintCallable 节点。

唯一的 BlueprintType 类是 `UDNAMeshVertexColorDataAsset`，提供一个查询函数：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetColorByMeshAndIndex` | 根据网格名和顶点 ID 查询颜色数据（用于面部颜色遮罩） | `UDNAMeshVertexColorDataAsset` |

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeDnaModule.h"
```

### 基本用法：同步导入 DNA 为 SkeletalMesh

```cpp
// 来源：InterchangeDnaModule.cpp - ImportSync()

#include "InterchangeDnaModule.h"
#include "DNAUtils.h"

// 1. 获取模块实例
FInterchangeDnaModule& DnaModule = FInterchangeDnaModule::GetModule();

// 2. 准备 DNAReader（从文件加载）
TArray<uint8> DNAData;
FFileHelper::LoadFileToArray(DNAData, TEXT("/path/to/character.dna"));
TSharedPtr<IDNAReader> DNAReader = ReadDNAFromBuffer(&DNAData, EDNADataLayer::All);

// 3. 同步导入（创建临时文件 → Interchange 导入 → 返回 SkeletalMesh）
USkeletalMesh* ImportedMesh = DnaModule.ImportSync(
    TEXT("MyMetaHumanFace"),           // 资产名
    TEXT("/Game/MetaHumans/MyFace"),    // 存储路径
    DNAReader,                          // DNA 数据
    nullptr                             // 可选：指定 Skeleton
);

// 4. 为导入的 Mesh 附加 DNA 数据（用于 RigLogic 驱动）
if (ImportedMesh)
{
    DnaModule.SetSkelMeshDNAData(ImportedMesh, DNAReader);
}
```

### 进阶用法：自定义 Payload 上下文

翻译器内部使用 `FDnaMeshPayloadContext` 和 `FDnaMorphTargetPayloadContext` 来按需提取网格和 BlendShape 数据。这些 Payload 在 `Translate()` 阶段注册，在 `GetMeshPayloadData()` 阶段被 Interchange 异步拉取。

关键流程：
1. `Translate()` 遍历 DNA 的所有 LOD 和 Mesh，创建 `UInterchangeMeshNode`（标记为 SkinnedMesh）
2. 为每个 Mesh 注册 `FDnaMeshPayloadContext`，记录 `DnaLodIndex` 和 `DnaMeshIndex`
3. 为每个 BlendShape 注册 `FDnaMorphTargetPayloadContext`，记录 `DnaMeshIndex`、`DnaMorphTargetIndex`、`DnaChannelIndex`
4. 当 Factory 请求 Mesh 数据时，`GetMeshPayloadData()` 从 PayloadContext 中提取 `FMeshDescription`

### 骨骼层级处理

DNA 文件中骨骼层级从 `spine_04` 开始，而 MetaHuman Archetype 骨架期望 `root → pelvis → spine_01 → spine_02 → spine_03 → ...` 的完整链条。翻译器在 `Translate()` 阶段自动补全这 5 个缺失关节（`DNAMissingJoints`），并使用硬编码的变换值：

```cpp
// 来源：MetaHumanInterchangeDnaTranslator.cpp - AddDNAMissingJoints()
// 补全的关节及其变换（从 Archetype SkeletalMesh 编辑器获取）
static const TArray<FString> DNAMissingJoints = { "root", "pelvis", "spine_01", "spine_02", "spine_03" };
```

### 材质槽映射

翻译器内置了 MetaHuman 面部网格到材质的映射表（`MaterialSlotsMapping`），支持 LOD0-LOD7 的头部、牙齿、眼睛、睫毛等子网格，以及身体网格。未在映射表中的网格自动使用 `{MeshName}_shader` 命名规则。

## Demo 示例

### 最小导入示例

```cpp
// MyDNAImporter.h
#pragma once

#include "CoreMinimal.h"

class FMyDNAImporter
{
public:
    static class USkeletalMesh* ImportDNAFile(const FString& InDNAFilePath, const FString& InOutputPath);
};
```

```cpp
// MyDNAImporter.cpp
#include "MyDNAImporter.h"
#include "InterchangeDnaModule.h"
#include "DNAUtils.h"
#include "Misc/FileHelper.h"

USkeletalMesh* FMyDNAImporter::ImportDNAFile(const FString& InDNAFilePath, const FString& InOutputPath)
{
    TArray<uint8> DNAData;
    if (!FFileHelper::LoadFileToArray(DNAData, *InDNAFilePath))
    {
        return nullptr;
    }

    TSharedPtr<IDNAReader> Reader = ReadDNAFromBuffer(&DNAData, EDNADataLayer::All);
    if (!Reader)
    {
        return nullptr;
    }

    FInterchangeDnaModule& Module = FInterchangeDnaModule::GetModule();
    USkeletalMesh* Mesh = Module.ImportSync(
        FPaths::GetBaseFilename(InDNAFilePath),
        InOutputPath,
        Reader
    );

    if (Mesh)
    {
        Module.SetSkelMeshDNAData(Mesh, Reader);
    }

    return Mesh;
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "InterchangeDNA",
    "RigLogicLib"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和内存管理 |
| `InterchangeCore` | Interchange 框架核心接口 |
| `InterchangeCommon` | Interchange 通用数据结构 |
| `InterchangeEngine` | Interchange 导入引擎 |
| `InterchangePipelines` | Interchange 导入管线 |
| `InterchangeImport` | Interchange 导入逻辑 |
| `InterchangeNodes` | Interchange 节点类型（MeshNode、SceneNode 等） |
| `LevelSequence` | 关卡序列支持 |
| `MeshDescription` | MeshDescription 网格描述框架 |
| `StaticMeshDescription` | 静态网格属性 |
| `SkeletalMeshDescription` | 骨骼网格蒙皮权重属性 |
| `RigLogicLib` | DNA 文件解析库（IDNAReader） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `Engine` | 引擎核心（私有依赖） |
| `RigLogicModule` | RigLogic 运行时模块（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-08-01 | `4d797bcdc6b4` | UnrealCodeFixup 批量修正 DLL 导出宏位置 |
| 2025-07-31 | `0f2260027766` | [MH-Plugin] 统一各插件的 Interchange 使用方式 |

### 维护评价

- **创建时间**：2025-07-31（约 0 年）
- **模块类型**：Editor（仅编辑器加载）
- **维护状态**：🆕 活跃维护中 — 作为 MetaHumanSDK 的核心模块，随 MetaHuman 工具链同步更新
- **实验性**：否（`IsExperimentalVersion=false`）
- **推荐**：✅ 推荐使用。这是 MetaHuman 工作流的标准 DNA 导入路径，与 UE5 的 Interchange 框架深度集成

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK/Source/InterchangeDNA)
- [MetaHumanSDK 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanSDK)
