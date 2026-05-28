# MetaHuman SDK

> Utilities and tools for working with MetaHumans in Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 数字人SDK |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `InterchangeDNA` (Runtime), `MetaHumanSDKEditor` (Editor), `MetaHumanSDKRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK) | |

## 用途

MetaHumanSDK 是 Epic 为 Unreal Engine 中的 MetaHuman 数字人工作流提供的官方 SDK。该插件解决的核心问题是：**如何将 MetaHuman DNA 数据（包含骨骼、网格、蒙皮权重等信息的专有格式）高效地导入并集成到 UE 的资产管线中**。

该插件从实验阶段（Experimental）正式移出，表明其 API 已趋于稳定。它依赖 UE 的 Interchange 框架来处理 DNA 格式的翻译和导入，提供了从 DNA 文件创建 SkeletalMesh、将 DNA 资产附加到骨骼网格体、以及管理顶点颜色映射等完整工具链。

简而言之：MetaHumanSDK 是连接 MetaHuman DNA 数据与 UE 资产系统的桥梁。

## 使用场景

- 你从 MetaHuman Creator 下载了数字人 DNA 数据，需要在 UE 中导入为 SkeletalMesh → 使用 `InterchangeDNA` 模块
- 你需要将 DNA Reader 的数据附加到已有的 SkeletalMesh 资产上（添加 DNAAssetUserData）→ 使用 `CreateAndAttachDNAToSkeletalMesh`
- 你需要通过 Interchange 管线批量导入 MetaHuman 角色 → 使用 `UMetaHumanInterchangeDnaTranslator`
- 你需要为 MetaHuman 的不同网格体分配逐顶点颜色数据（用于自定义着色或调试）→ 使用 `UDNAMeshVertexColorDataAsset`
- 你需要自定义 DNA 导入配置（骨骼映射、缺失关节处理等）→ 使用 `FDNAConfig` 和翻译器

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetColorByMeshAndIndex` | 根据网格体名称和顶点索引获取顶点颜色 | `UDNAMeshVertexColorDataAsset` |

### 使用示例（蓝图描述）

**查询顶点颜色**：
1. 获取对 `UDNAMeshVertexColorDataAsset` 数据资产的引用（例如通过变量或资产引用）
2. 调用 `GetColorByMeshAndIndex`，传入网格体名称字符串和顶点索引整数
3. 返回 `FLinearColor`，如果未找到匹配的网格体或顶点索引越界，返回默认白色 (1,1,1,1)

**FMeshVertexColorData 结构体属性**（BlueprintReadWrite）：
- `MeshName`：对应 SkeletalMesh 的名称
- `Colors`：该网格体所有顶点的颜色数组

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeDnaModule.h"
#include "MetaHumanInterchangeDnaTranslator.h"
#include "MetaHumanDNAImportColorMap.h"
```

### 基本用法：将 DNA 数据附加到 SkeletalMesh

从 `FInterchangeDnaModule` 的公共 API 提取：

```cpp
#include "InterchangeDnaModule.h"
#include "Engine/SkeletalMesh.h"

// 获取 InterchangeDNA 模块实例
FInterchangeDnaModule& DnaModule = FInterchangeDnaModule::GetModule();

// 将 DNA 数据附加到已有的 SkeletalMesh
// InDNAReader: 从 .dna 文件加载的 DNA Reader
DnaModule.CreateAndAttachDNAToSkeletalMesh(MySkeletalMesh, SharedDNAReader);
```

来源：`Source/InterchangeDNA/Public/InterchangeDnaModule.h`

### 进阶用法：同步导入 DNA 为 SkeletalMesh

```cpp
#include "InterchangeDnaModule.h"

FInterchangeDnaModule& DnaModule = FInterchangeDnaModule::GetModule();

// 配置导入参数
FDNAConfig Config;
// ... 根据需要设置 Config

// 同步导入：指定资产名称、路径、DNA Reader、目标 Skeleton
USkeletalMesh* ImportedMesh = DnaModule.ImportSync(
    TEXT("MyMetaHuman_Body"),          // 新资产名称
    TEXT("/Game/MetaHumans/MyChar"),   // 导入路径
    SharedDNAReader,                    // TSharedPtr<IDNAReader>
    TargetSkeleton,                     // TSoftObjectPtr<USkeleton>
    Config                              // 可选的 DNA 配置
);
```

来源：`Source/InterchangeDNA/Public/InterchangeDnaModule.h`

### 通过 Interchange 翻译器使用

```cpp
#include "MetaHumanInterchangeDnaTranslator.h"

// UMetaHumanInterchangeDnaTranslator 通过 Interchange 管线自动参与导入流程
// 通常不需要直接实例化，而是在 Interchange 导入管线中注册使用
// 支持的格式可通过 GetSupportedFormats() 查询
// 线程安全：IsThreadSafe() 返回 true（可多线程翻译）
```

## Demo 示例

```cpp
// MyMetaHumanImporter.h
#pragma once

#include "CoreMinimal.h"

class FMyMetaHumanImporter
{
public:
    void ImportMetaHumanFromDNA(const FString& InDNAFilePath, USkeleton* InTargetSkeleton);
};
```

```cpp
// MyMetaHumanImporter.cpp
#include "MyMetaHumanImporter.h"
#include "InterchangeDnaModule.h"
#include "Engine/SkeletalMesh.h"

void FMyMetaHumanImporter::ImportMetaHumanFromDNA(const FString& InDNAFilePath, USkeleton* InTargetSkeleton)
{
    // 获取模块实例
    FInterchangeDnaModule& DnaModule = FInterchangeDnaModule::GetModule();

    // 注意：实际使用中需要先通过 DNA 库加载 IDNAReader
    // TSharedPtr<IDNAReader> DNAReader = LoadDNAFromFile(InDNAFilePath);

    // 方式一：同步导入为新的 SkeletalMesh
    /*
    USkeletalMesh* NewMesh = DnaModule.ImportSync(
        FPaths::GetBaseFilename(InDNAFilePath),
        TEXT("/Game/ImportedMetaHumans"),
        DNAReader,
        TSoftObjectPtr<USkeleton>(InTargetSkeleton)
    );
    */

    // 方式二：将 DNA 附加到已有的 SkeletalMesh
    /*
    if (USkeletalMesh* ExistingMesh = FindExistingMesh())
    {
        DnaModule.CreateAndAttachDNAToSkeletalMesh(ExistingMesh, DNAReader);
    }
    */
}
```

## 模块依赖

从头文件推断的依赖关系（建议查看各模块 Build.cs 确认）：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 翻译器基类 `UInterchangeTranslatorBase` |
| `InterchangeEngine` | Interchange 导入引擎集成 |
| `InterchangeNodes` | `UInterchangeBaseNodeContainer` 等节点容器 |
| `DNAInterchange` / `DNA` | `IDNAReader` 接口及 DNA 数据处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `5c0dc0e5` | [MHSDK] Remove the VersionInfo.txt existence check when discovering MetaHuman character assemblies a | 移除发现 MetaHuman 角色装配体时对 VersionInfo.txt 的存在性检查 |
| 2026-05-21 | `418099aa` | Fix the incorrectly converted parent bones for Legacy DNAConfig case | 修复 Legacy DNAConfig 模式下父骨骼错误转换的问题 |
| 2026-05-14 | `d477b10c` | [MHSDK] Replace path-based related-asset filtering in MetaHuman Manager with dependency walking now | MetaHuman Manager 中资产关联过滤从路径匹配改为依赖图遍历 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `c0e92a2b` | [MHSDK] Fix MetaHuman skeletal clothing verification reading incorrect texture dimensions by ensurin | 修复骨骼衣物验证中读取错误纹理尺寸的问题 |

### 维护评价

**活跃维护**。该插件于 2025 年 4 月从实验阶段正式移出，创建时间仅约 1 年。近期（2026 年 5 月）提交非常密集，一周内有 5 次提交，内容涵盖：
- Bug 修复（骨骼转换、纹理尺寸验证、浮点精度警告）
- 架构改进（依赖图遍历替代路径匹配）
- 流程简化（移除不必要的文件检查）

作为 Epic 官方维护的 MetaHuman 核心基础设施，该插件处于**持续活跃开发**状态，推荐在 MetaHuman 工作流中使用。需注意该插件仍可能有 API 变动，建议关注版本升级时的 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立测试目录）