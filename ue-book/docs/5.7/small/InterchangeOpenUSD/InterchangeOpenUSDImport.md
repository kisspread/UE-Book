# Interchange OpenUSD

> Allows translation of OpenUSD files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | Interchange USD 翻译器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeOpenUSDEditor` (Runtime), `InterchangeOpenUSDImport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenUSD) | |

---

## 用途

Interchange OpenUSD 插件是 Unreal Engine 新一代导入框架（Interchange）的一个扩展，专门用于导入 Universal Scene Description（USD）文件。它通过实现 Interchange 的翻译器（Translator）、工厂管道（Pipeline）和上下文（Context）等接口，将 USD 场景转换为 Interchange 内部节点图，进而支持将 USD 资产（网格、材质、纹理、动画、体积、毛发、音频等）导入到 UE 项目中。

该插件的作用等同于旧版 USD Importer（`USDImporter` 插件）在 Interchange 框架内的现代化实现。它解决的核心问题是：如何在保证互操作性的前提下，利用 Interchange 的统一管道来支持 USD 格式的导入，同时保留 USD 原有的高级特性（如时间采样、变体集、LOD、多材质绑定等）。

**为什么存在？**  
- Interchange 框架旨在替代传统的 FBX 和 OBJ 导入器，提供更灵活、可扩展的资产导入管线。  
- USD 作为行业标准场景描述格式，需要无缝集成到该框架中。  
- 通过插件方式提供，避免核心 Interchange 模块因支持具体格式而膨胀。

---

## 使用场景

- 你正在开发影视级或工业级应用，需要导入 Pixar USD 或 USDA/USDC/USDZ 文件。  
- 你需要将带有复杂材质、毛发的 USD 角色导入 UE，并保持动画绑定。  
- 你需要在导入时对 USD 进行过滤（按目的、渲染上下文、材质目的等）和后处理。  
- 你希望通过 Interchange 的高级功能（如自定义管道、预览、多源数据）来管理 USD 导入流程。

---

## 蓝图用法

### 核心节点（蓝图可调用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetStageId` | 获取当前绑定 USD 舞台在 `UsdUtils` 的全局舞台缓存中的 ID | `UInterchangeUsdContext` |
| `SetStageId` | 设置一个舞台 ID，使 Interchange 导入使用该舞台 | `UInterchangeUsdContext` |

**说明**：  
`UInterchangeUsdContext` 是一个蓝图类型，常用于 Python 导入或自定义管道脚本。它不直接存储舞台对象，而是通过缓存 ID 引用，以便 Python 侧操纵舞台后仍能被 Interchange 使用。

### 管道属性（蓝图可读写）

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `PipelineDisplayName` | FString | 管道显示名称，用于识别 | `UInterchangeUsdPipeline` |
| `GeometryPurpose` | int32 (bitmask) | 按 USD 目的过滤几何 prim，位掩码对应 `EUsdPurpose` | `UInterchangeUsdPipeline` |
| `ImportPrimvars` | EInterchangeUsdPrimvar | 控制 primvar 如何附加到 MeshDescription（如烘焙、不导入等） | `UInterchangeUsdPipeline` |
| `SubdivisionLevel` | int32 | 细分面细分等级（0 表示不细分），最大等级受 cvar 限制 | `UInterchangeUsdPipeline` |
| `bImportPseudoRoot` | bool | 是否导入舞台伪根节点（文件名对应的场景根） | `UInterchangeUsdPipeline` |
| `bGeneratePrimvarCompatibleMaterials` | bool | 是否生成与 primvar-UV 索引映射兼容的材质实例 | `UInterchangeUsdPipeline` |

这些属性可在 “Content Browser → Interchange 导入选项 → USD 管道” 中直接编辑。同时，你也可以在蓝图中创建管道对象并修改这些属性，然后应用到 Interchange 导入任务中。

---

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeOpenUSDImportModule.h"
#include "InterchangeUSDTranslator.h"
#include "InterchangeUSDPipeline.h"
#include "InterchangeUsdContext.h"
```

### 基本用法

**1. 启动导入（在模块中注册翻译器）**

```cpp
// 在模块 StartupModule 中确保翻译器已被注册
void FInterchangeOpenUSDImportModule::StartupModule()
{
    // 内部注册由 Interchange 框架自动完成（通过模块加载时生成的静态注册）
}
```

**2. 使用 USD 上下文加载舞台**

```cpp
#include "InterchangeUsdContext.h"
#include "UsdWrappers/SdfLayer.h"
#include "UsdWrappers/UsdStage.h"

void LoadUSDForInterchange(const FString& FilePath)
{
    UInterchangeUsdContext* Context = NewObject<UInterchangeUsdContext>();
    
    // 方式一：通过文件路径加载并设置
    UE::FUsdStage Stage = UE::FUsdStage::Open(UE::FSdfLayer::FindOrOpen(*FilePath));
    Context->SetUsdStage(Stage);
    
    // 方式二：如果已有舞台缓存 ID
    // int64 StageId = Context->GetStageId();
    // Context->SetStageId(StageId);
    
    // 设置外部 InfoCache（可选，用于加速）
    // FUsdInfoCache Cache;
    // Context->SetExternalInfoCache(Cache);
}
```

**3. 自定义管道执行过滤**

```cpp
#include "InterchangeUSDPipeline.h"
#include "InterchangeManager.h"

void SetupUSDPipeline(UInterchangeSourceData* SourceData)
{
    UInterchangeUsdPipeline* Pipeline = NewObject<UInterchangeUsdPipeline>();
    
    // 配置过滤选项
    Pipeline->GeometryPurpose = (int32)EUsdPurpose::Default | (int32)EUsdPurpose::Render;
    Pipeline->SubdivisionLevel = 1;
    Pipeline->bImportPseudoRoot = false;
    Pipeline->ImportPrimvars = EInterchangeUsdPrimvar::Bake;
    Pipeline->bGeneratePrimvarCompatibleMaterials = true;
    
    // 将管道添加到 Interchange 管理器
    UInterchangeManager* Manager = UInterchangeManager::GetInterchangeManager();
    TArray<UInterchangePipelineBase*> Pipelines;
    Pipelines.Add(Pipeline);
    
    // 启动导入（假设已创建任务）
    // FImportAssetParameters Params;
    // Params.OverridePipelines = Pipelines;
    // Manager->ImportAsset(SourceData, Params);
}
```

**4. 设置翻译器配置**

`UInterchangeUsdTranslatorSettings` 提供精细控制，如渲染上下文、材质目的、舞台选项、原生属性/元数据导入等：

```cpp
UInterchangeUsdTranslatorSettings* Settings = NewObject<UInterchangeUsdTranslatorSettings>();
Settings->RenderContext = FName("mtlx");  // MaterialX 渲染上下文
Settings->MaterialPurpose = FName("preview");
Settings->bOverrideStageOptions = true;
Settings->StageOptions.StartTime = 0.0f;
Settings->StageOptions.EndTime = 0.0f;   // 只导入第一帧
Settings->bTranslatePrimAttributes = true;
Settings->AttributeRegexFilter = "userProperties:.*";
Settings->bTranslatePrimMetadata = true;
Settings->MetadataRegexFilter = "customData";
```

**来源**：`Engine/Plugins/Interchange/Extensions/OpenUSD/Source/Import/Public/InterchangeUsdTranslator.h`

---

## Demo 示例

以下是一个最小化可编译的控制台示例，演示如何通过 Interchange USD 插件加载舞台并提取信息。假设项目已启用 Interchange 插件。

**UsdInterchangeDemo.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "UsdInterchangeDemo.generated.h"

UCLASS()
class UUsdInterchangeDemo : public UObject
{
    GENERATED_BODY()
public:
    static void Run(const FString& USDFilePath);
};
```

**UsdInterchangeDemo.cpp**

```cpp
#include "UsdInterchangeDemo.h"
#include "InterchangeUsdContext.h"
#include "InterchangeUSDTranslator.h"
#include "InterchangeUSDPipeline.h"
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/SdfLayer.h"

void UUsdInterchangeDemo::Run(const FString& USDFilePath)
{
    // 1. 加载 USD 舞台
    UE::FUsdStage Stage = UE::FUsdStage::Open(*USDFilePath);
    if (!Stage)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD file: %s"), *USDFilePath);
        return;
    }

    // 2. 创建上下文并关联舞台
    UInterchangeUsdContext* Ctx = NewObject<UInterchangeUsdContext>();
    Ctx->SetUsdStage(Stage);
    int64 StageId = Ctx->GetStageId();
    UE_LOG(LogTemp, Log, TEXT("Stage cached with ID: %lld"), StageId);

    // 3. 创建翻译器设置
    UInterchangeUsdTranslatorSettings* Settings = NewObject<UInterchangeUsdTranslatorSettings>();
    Settings->bTranslatePrimAttributes = false;  // 避免导入大量原生属性
    Settings->bTranslatePrimMetadata = true;
    Settings->MetadataRegexFilter = "customData";

    // 4. 创建管道并配置
    UInterchangeUsdPipeline* Pipeline = NewObject<UInterchangeUsdPipeline>();
    Pipeline->SubdivisionLevel = 0;
    Pipeline->bImportPseudoRoot = false;
    Pipeline->ImportPrimvars = EInterchangeUsdPrimvar::Bake;

    // 5. 在实际项目中，应通过 UInterchangeManager::ImportAsset 启动导入
    // 此处仅为示例，展示对象创建流程
    UE_LOG(LogTemp, Log, TEXT("USD Interchange demo pipeline ready."));
}
```

**注意**：完整导入需要 `UInterchangeManager` 和 `UInterchangeSourceData` 的配合，此处仅展示对象构造。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架核心：节点容器、翻译器基类、工厂管道基础 |
| `InterchangeEngine` | Interchange 引擎：管理器、导入任务处理 |
| `UnrealUSDWrapper` | USD C++ 绑定库（PXR 或 USD 原生 API） |
| `USDClasses` | USD 通用类（如 `FUsdInfoCache`、`EUsdPurpose`） |
| `USDUtilities` | USD 工具函数（舞台选项、primvar 处理） |
| `USDStageOptions` | 舞台时间范围、帧率等设置 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore 等。

---

## 维护状态

### 近期更新

```
2025-12-18  3f562d0e  Fixed crash when Interchange stack names have been modified.
2025-10-16  09310c6c  [USD Interchange] Nanite Assembly reimport fixes
2025-10-03  24fcc14e  [Backout] - CL46528816
2025-10-03  a8f28318  Interchange USD: Set some min/max for the SubdivisionLevel property editor similar to USD legacy.
2025-10-02  56e5b338  USD: Fix duplicate LOCTEXT key.
```

### 维护评价

该插件创建于 2025 年 10 月，是全新的实验性功能。最近一次 commit 距今不到 1 个月，主要是修复崩溃和推进功能（Nanite 重导入支持）。虽然标记为实验性，但开发活跃，修复及时。适合用于非生产性测试或早期体验 USD 在 Interchange 框架下的导入功能。注意：当前版本（1.0）仍处于实验阶段，可能存在 API 变化或未覆盖功能。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenUSD)
- [官方文档](https://docs.unrealengine.com/5.7/InterchangeUSD)（待补充）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenUSD/Source/Import/Tests)（若有）