# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 互换导入导出框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `InterchangeAnalytics` (Runtime), `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 2022-03-15 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange) | |

## 用途

Interchange Framework 是 UE5 用来替代旧版 FBX 导入管线的**全新资产导入/导出框架**。旧系统将 FBX 解析、场景图构建、资产创建逻辑耦合在一起，难以扩展和自定义。Interchange 将整个流程拆分为三个独立阶段：

1. **解析（Parser）**：将文件格式（FBX、glTF 等）转换为统一的**中间节点图（Interchange Graph）**，与具体资产类型无关
2. **管线（Pipeline）**：对节点图进行过滤、修改、合并等操作——用户可以插入自定义逻辑
3. **工厂（Factory）**：根据处理后的节点图创建实际的 UE 资产（StaticMesh、SkeletalMesh、Texture、Material 等）

这种架构使得添加新文件格式只需编写 Parser，添加新资产类型只需编写 Factory，两者通过标准化的节点图解耦。同时支持**导入和导出**双向操作，且支持异步处理以避免阻塞编辑器。

## 使用场景

- 你需要导入 FBX、glTF、USD 等 3D 模型文件到 UE → Interchange 是默认的导入通道（UE5.1+ 已替代旧 FBX Importer）
- 你需要自定义导入行为（如批量修改材质参数、自动设置 LOD 策略）→ 编写自定义 Pipeline 插入导入流程
- 你需要从 UE 导出资产到其他格式 → 使用 Interchange Export 系统
- 你需要支持一种全新的文件格式（如自定义的模型格式）→ 编写 Parser 模块将其转换为 Interchange 节点图即可
- 你需要追踪导入/导出的分析数据（哪些资产类型被导入、使用了哪些 Pipeline）→ 使用 InterchangeAnalytics 模块

---

> **注意**：本文档聚焦于 **InterchangeAnalytics** 子模块的 API。Interchange 是超大型插件（753+ 源文件，13 个模块），完整文档需按子模块拆分。本页面作为汇总入口，各子模块 API 文档详见下方链接。

## 子模块概览

| 模块 | 用途 |
|---|---|
| **InterchangeAnalytics** | 导入/导出分析追踪（Pipeline 使用统计、资产类型频率等） |
| **InterchangeCommon** | 公共工具类与类型定义 |
| **InterchangeDispatcher** | 异步任务调度器，协调导入/导出流程 |
| **InterchangeExport** | 资产导出功能实现 |
| **InterchangeFactoryNodes** | 工厂节点定义（对应各资产类型的创建逻辑） |
| **InterchangeImport** | 资产导入核心逻辑 |
| **InterchangeMessages** | 模块间消息通信系统 |
| **InterchangeNodes** | 中间节点图的节点类型定义（公共 API） |
| **InterchangeCommonParser** | 通用解析器基础设施 |
| **InterchangeFbxParser** | FBX 文件格式解析器 |
| **GLTFCore** | glTF 文件格式解析核心 |
| **InterchangePipelines** | 内置 Pipeline 实现（纹理、材质、网格体等处理逻辑） |
| **Draco** | 第三方 Draco 压缩库（用于 glTF 的 Mesh 压缩） |

---

## 蓝图用法

### 核心节点（InterchangeAnalytics）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterAssetType` | 注册资产类型以进行分析追踪 | `FInterchangeAnalyticsAssetTypeTracker` |
| `GetAssetTypeFrequenceMap` | 获取资产类型频率统计表 | `FInterchangeAnalyticsAssetTypeTracker` |
| `AppendAssetTypeFrequenceMap` | 追加资产类型频率到已有统计表 | `FInterchangeAnalyticsAssetTypeTracker` |

`UInterchangeAnalyticsHandlerDefault` 标记为 `BlueprintType, Blueprintable`，可作为蓝图基类自定义分析发送逻辑。

### 使用示例

**自定义 Analytics Handler**：
1. 创建一个新蓝图类，父类选择 `UInterchangeAnalyticsHandlerDefault`
2. 覆写 `Send` 事件，在其中添加自定义分析逻辑（如发送到自定义后端）
3. 在项目设置中将自定义 Handler 注册为 Interchange 的分析处理器

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeAnalyticsModule.h"
#include "InterchangeAnalyticsHandlerDefault.h"
#include "InterchangeAnalyticsAssetTypeTracker.h"
```

### 基本用法 — 注册和查询资产类型追踪

```cpp
// 注册自定义资产类型以参与分析追踪
FInterchangeAnalyticsAssetTypeTracker::RegisterAssetType(UMyCustomAsset::StaticClass(), TEXT("MyCustomAsset"));

// 查询已导入对象的资产类型频率
TArray<TObjectPtr<UObject>> ImportedObjects = GetImportedObjects();
TMap<FString, int32> FreqMap = FInterchangeAnalyticsAssetTypeTracker::GetAssetTypeFrequenceMap(ImportedObjects);

// 遍历结果
for (const auto& [TypeName, Count] : FreqMap)
{
    UE_LOG(LogTemp, Log, TEXT("AssetType '%s': %d instances"), *TypeName, Count);
}
```

### 进阶用法 — 自定义分析 Handler

```cpp
// 从 UInterchangeAnalyticsHandlerDefault 派生自定义 Handler
UCLASS()
class UMyAnalyticsHandler : public UInterchangeAnalyticsHandlerDefault
{
    GENERATED_BODY()
    
public:
    virtual void Send(const TArray<UInterchangePipelineBase*>& Pipelines, const int32 AsyncHelperUniqueId) override
    {
        // 先调用父类实现（记录 Pipeline 属性到 AnalyticsAttributes）
        Super::Send(Pipelines, AsyncHelperUniqueId);
        
        // 自定义：将 Pipeline 使用信息发送到外部系统
        for (const UInterchangePipelineBase* Pipeline : Pipelines)
        {
            if (Pipeline)
            {
                SendCustomReport(TEXT("PipelineUsed"), Pipeline->GetName());
            }
        }
    }
    
    virtual void Send(const FInterchangeImportResultAnalyticsInfo& ImportResultAnalyticsInfo) override
    {
        // 自定义：记录导入结果到数据库
        LogImportResult(ImportResultAnalyticsInfo);
    }
};
```

### 进阶用法 — 模块可用性检查

```cpp
// 安全地检查 Analytics 模块是否已加载
if (IInterchangeAnalyticsModule::IsAvailable())
{
    IInterchangeAnalyticsModule& AnalyticsModule = IInterchangeAnalyticsModule::Get();
    // 使用模块接口...
}
```

## Demo 示例

```cpp
// MyInterchangeAnalytics.h
#pragma once

#include "CoreMinimal.h"
#include "InterchangeAnalyticsHandlerDefault.h"
#include "MyInterchangeAnalytics.generated.h"

UCLASS()
class MYPROJECT_API UMyInterchangeAnalytics : public UInterchangeAnalyticsHandlerDefault
{
    GENERATED_BODY()

public:
    virtual void Send(const FInterchangeImportResultAnalyticsInfo& ImportResultAnalyticsInfo) override;
    
    void PrintImportSummary(const FInterchangeImportResultAnalyticsInfo& Info) const;
};
```

```cpp
// MyInterchangeAnalytics.cpp
#include "MyInterchangeAnalytics.h"

void UMyInterchangeAnalytics::Send(const FInterchangeImportResultAnalyticsInfo& ImportResultAnalyticsInfo)
{
    // 调用父类默认行为
    Super::Send(ImportResultAnalyticsInfo);
    
    // 打印导入摘要
    PrintImportSummary(ImportResultAnalyticsInfo);
}

void UMyInterchangeAnalytics::PrintImportSummary(const FInterchangeImportResultAnalyticsInfo& Info) const
{
    UE_LOG(LogTemp, Log, TEXT("Interchange import completed. Asset types imported:"));
    
    // 使用资产类型追踪器统计导入结果
    TMap<FString, int32> FreqMap;
    for (const auto& Pair : Info.ImportedObjects)
    {
        // 根据实际 FInterchangeImportResultAnalyticsInfo 结构访问数据
        UE_LOG(LogTemp, Log, TEXT("  - %s"), *Pair.Key);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCommon` | Interchange 公共类型和工具（所有子模块的基础） |
| `InterchangeNodes` | 节点图的节点类型定义（Parser 和 Factory 的共享数据结构） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。Analytics 模块额外依赖项目级的 `Analytics` 模块进行事件上报。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 为 USD 预生成实现骨骼和物理资产的追踪 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 的本地化警告 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 重导入时重置 LOD 模型以更新骨骼绑定和映射 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 将 uFBX 解析器恢复为实验性功能 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects | 修复导入对象列表中空指针导致的崩溃 |

### 维护评价

Interchange Framework 是 **Epic Games 积极维护的核心基础设施**。作为 UE5 资产导入/导出的默认管线，它处于持续开发状态：

- **活跃维护**：近期（2026 年 5 月）有多次实质性更新，包括 USD 支持改进、bug 修复、新解析器引入
- **核心地位**：已替代旧版 FBX Importer 成为 UE5 默认导入通道，不会被废弃
- **仍在扩展**：支持的格式不断增加（FBX、glTF、USD），且架构支持第三方扩展
- **规模庞大**：753+ 源文件、13 个子模块，适合按需阅读特定子模块
- **推荐使用**：✅ 如果你需要自定义导入/导出流程，Interchange 是唯一推荐的框架。对于 Analytics 子模块，除非你需要自定义分析上报逻辑，否则无需直接使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/interchange-framework-in-unreal-engine/)