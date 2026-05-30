# Cinematic Assembly Tools (CAT)

> CAT is a suite of cinematic pipeline tools for shot management and linear content creation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 影视组装工具 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器UI） |
| 模块 | `CineAssemblyTools` (Runtime), `CineAssemblyToolsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CinematicAssemblyTools) | |

## 用途

Cinematic Assembly Tools（CAT）是一个面向虚拟制片和线性内容创作的影视管线工具集。它解决了以下核心问题：

1. **镜头/序列的结构化管理**：传统的 LevelSequence 只是一个序列容器，缺乏元数据、层级关系和资产关联。CAT 引入了 **CineAssembly**（影视组装体），它继承自 LevelSequence，但增加了元数据系统、关联资产管理、子组装体层级，以及基于 Schema 的模板化创建。

2. **模板化的资产创建流程**：通过 **CineAssemblySchema**（组装体模式），用户可以定义组装体的结构模板——包含哪些子序列、关联哪些资产（如关卡、材质等）、使用什么命名规则。每次基于 Schema 创建组装体时，都会自动生成一致的资产结构。

3. **影视制作（Production）的项目级管理**：CAT 提供了 Production 设置系统，可以为不同影视项目配置帧率、起始帧、命名规则、文件夹模板、资产默认名等，并支持在多个 Production 之间切换。

4. **统一的镜头管线工作流**：从创建镜头、录制（Take Recorder 集成）、编辑（Sequencer 集成）、到复制和批量管理，CAT 提供了完整的端到端镜头管理管线。

## 使用场景

- 你在做一个**线性叙事项目**（如动画短片、过场动画），需要管理大量镜头和子序列 → 用 CAT 的 CineAssembly 系统
- 你需要**标准化镜头创建流程**，确保每个镜头都有相同的关联资产和命名规范 → 用 CineAssemblySchema 模板
- 你在管理**多个影视项目**，每个项目有不同的帧率、命名规则和文件夹结构 → 用 Production 设置系统
- 你需要通过**蓝图或 Python 脚本**批量创建和管理镜头资产 → 用 CAT 的 BlueprintCallable 函数库
- 你在使用 **Take Recorder** 录制表演，希望录制结果自动关联到组装体结构中 → 用 Take Recorder 集成

## 核心概念

### CineAssembly（组装体）

CineAssembly 继承自 LevelSequence，是一个结构化的镜头/序列容器。每个组装体包含：

- **元数据（Metadata）**：键值对形式的自定义数据，支持命名令牌（Naming Tokens）动态求值
- **子组装体（SubAssemblies）**：嵌套的子序列，可以是模板型（基于 Schema 创建）或引用型（引用已有序列）
- **关联资产（Associated Assets）**：与组装体一起创建的资产（如关卡），由 Schema 定义
- **文件夹结构**：组装体创建时自动生成的文件夹层级

### CineAssemblySchema（组装体模式）

Schema 是组装体的模板定义，决定了基于它创建的组装体的结构：
- 默认命名规则（支持令牌占位符）
- 子序列模板和引用
- 关联资产描述（类型、路径、模板资产）
- 元数据字段定义
- 缩略图
- 父 Schema 限制（控制组装体层级关系）

### Production（影视制作）

Production 是项目级的配置单元，包含：
- 帧率、起始帧
- 子序列优先级（TopDown/BottomUp）
- 命名令牌命名空间过滤
- 资产默认命名
- 文件夹模板层级
- 可扩展数据（Extended Data）

## 蓝图用法

### 核心节点——组装体管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateAssembly` | 使用 Schema、关卡、元数据创建新的组装体资产 | `UCineAssemblyEditorFunctionLibrary` |
| `CreateAssemblyToConfigure` | 创建内存中的临时组装体，可进一步配置后通过 `FinalizeConfiguredAssembly` 持久化 | `UCineAssemblyEditorFunctionLibrary` |
| `FinalizeConfiguredAssembly` | 将临时组装体持久化为真实资产 | `UCineAssemblyEditorFunctionLibrary` |
| `OpenAssembly` | 在 Sequencer 中打开组装体，可选同时打开关联关卡 | `UCineAssemblyEditorFunctionLibrary` |
| `OpenAssociatedLevel` | 打开组装体的关联关卡 | `UCineAssemblyEditorFunctionLibrary` |
| `DuplicateAssembly` | 复制组装体到指定路径，支持配置子序列和关联资产的复制策略 | `UCineAssemblyEditorFunctionLibrary` |
| `DuplicateAssemblyToConfigure` | 创建内存中的临时复制，用于进一步配置 | `UCineAssemblyEditorFunctionLibrary` |
| `FinalizeDuplicateAssembly` | 持久化临时复制的组装体 | `UCineAssemblyEditorFunctionLibrary` |
| `FindAssembliesBySchema` | 按 Schema 查找所有已创建的组装体资产 | `UCineAssemblyEditorFunctionLibrary` |

### 核心节点——Schema 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateSchema` | 创建新的组装体模式资产，可配置名称、路径、描述、缩略图等 | `UCineAssemblyEditorFunctionLibrary` |
| `AddSubAssemblyTemplate` | 为 Schema 添加模板子组装体（创建组装体时会基于模板对象初始化新序列） | `UCineAssemblyEditorFunctionLibrary` |
| `AddSubAssemblyReference` | 为 Schema 添加引用子组装体（创建组装体时直接引用已有序列） | `UCineAssemblyEditorFunctionLibrary` |
| `AddAssociatedAsset` | 为 Schema 添加关联资产描述（如关卡），创建组装体时自动生成 | `UCineAssemblyEditorFunctionLibrary` |
| `RemoveAssociatedAsset` | 从 Schema 移除关联资产描述 | `UCineAssemblyEditorFunctionLibrary` |

### 核心节点——Production 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetProductionSettings` | 获取 Production 设置对象 | `UProductionFunctionLibrary` |
| `GetAllProductions` | 获取所有可用的影视制作配置 | `UProductionFunctionLibrary` |
| `GetActiveProduction` | 获取当前激活的制作配置 | `UProductionFunctionLibrary` |
| `SetActiveProduction` | 设置激活的制作配置 | `UProductionFunctionLibrary` |
| `AddProduction` | 添加新的制作配置 | `UProductionFunctionLibrary` |
| `DeleteProduction` | 删除指定制作配置 | `UProductionFunctionLibrary` |
| `RenameProduction` | 重命名制作配置 | `UProductionFunctionLibrary` |
| `GetProductionExtendedData` | 获取制作的扩展数据 | `UProductionFunctionLibrary` |
| `SetProductionExtendedData` | 设置制作的扩展数据 | `UProductionFunctionLibrary` |

### 核心节点——命名令牌与元数据

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateTokenString` | 使用组装体上下文对令牌字符串求值（如 `{cat.shot}` → `shot_001`） | `UCineAssemblyEditorFunctionLibrary` |
| `BuildTokenContext` | 为组装体构建命名令牌上下文对象 | `UCineAssemblyEditorFunctionLibrary` |

### 核心节点——关联资产描述操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSchemaAssociatedAssetDesc` | 获取 Schema 上指定 ID 的关联资产描述 | `UCineAssemblyEditorFunctionLibrary` |
| `GetAssemblyAssociatedAssetDesc` | 获取组装体上指定 ID 的关联资产描述 | `UCineAssemblyEditorFunctionLibrary` |
| `GetSchemaAssociatedAssetDescs` | 获取 Schema 上所有关联资产描述 | `UCineAssemblyEditorFunctionLibrary` |
| `GetAssemblyAssociatedAssetDescs` | 获取组装体上所有关联资产描述 | `UCineAssemblyEditorFunctionLibrary` |
| `SetAssociatedAssetClass` | 设置关联资产的类类型（仅 Schema） | `UCineAssemblyEditorFunctionLibrary` |
| `SetAssociatedAssetRelativePath` | 设置关联资产的相对路径（仅 Schema） | `UCineAssemblyEditorFunctionLibrary` |
| `SetAssociatedAssetTemplate` | 设置关联资产的模板资产（仅 Schema） | `UCineAssemblyEditorFunctionLibrary` |

### 事件委托

| 委托 | 说明 | 所在类 |
|---|---|---|
| `OnAssemblyCreated` | 组装体资产创建完成时广播 | `UCineAssemblyEditorSubsystem` |
| `OnSchemaCreated` | Schema 资产创建完成时广播 | `UCineAssemblyEditorSubsystem` |
| `OnAssemblyDuplicated` | 组装体复制完成时广播 | `UCineAssemblyEditorSubsystem` |
| `OnAssemblyMetadataChanged` | 组装体元数据修改时广播 | `UCineAssemblyEditorSubsystem` |
| `OnProductionCreated` | 新的制作配置创建时广播 | `UProductionSettings` |
| `OnProductionSettingsChanged` | 制作配置的设置修改时广播 | `UProductionSettings` |
| `OnActiveProductionSet` | 激活的制作配置变更时广播 | `UProductionSettings` |

### 使用示例（蓝图描述）

**创建一个基于 Schema 的新组装体：**

1. 从内容浏览器获取一个 `UCineAssemblySchema` 资产引用
2. 拖入 `CreateAssembly` 节点，连接 Schema 输入
3. 可选连接关卡软引用（`TSoftObjectPtr<UWorld>`）
4. 可选提供元数据 Map（`TMap<FString, FString>`），用于填充命名令牌
5. 指定内容浏览器创建路径
6. 节点输出即为新创建的 `UCineAssembly` 资产

**配置 Production 并创建文件夹模板：**

1. 拖入 `GetActiveProduction` 确认当前有激活的制作配置
2. 使用 `SetActiveProduction` 切换到目标制作
3. 通过 `UProductionSettings` 的引用设置帧率和起始帧
4. 文件夹模板在 Production Wizard UI 中配置

## C++ 用法

### 头文件引入

```cpp
// 组装体功能库（创建、复制、管理组装体）
#include "CineAssemblyEditorFunctionLibrary.h"

// Production 功能库（管理影视制作配置）
#include "ProductionFunctionLibrary.h"

// Production 设置（获取/修改制作配置）
#include "ProductionSettings.h"

// 编辑器模块接口（注册扩展）
#include "ICineAssemblyToolsEditorModule.h"

// 编辑器子系统（监听事件）
#include "CineAssemblyEditorSubsystem.h"
```

### 基本用法：创建组装体

```cpp
// 来源: Public/CineAssemblyEditorFunctionLibrary.h

// 获取 Schema 资产
UCineAssemblySchema* MySchema = LoadObject<UCineAssemblySchema>(nullptr, TEXT("/Game/Cinematic/MySchema"));

// 准备元数据（用于命名令牌求值）
TMap<FString, FString> Metadata;
Metadata.Add(TEXT("shot"), TEXT("001"));
Metadata.Add(TEXT("sequence"), TEXT("A"));

// 创建组装体
UCineAssembly* NewAssembly = UCineAssemblyEditorFunctionLibrary::CreateAssembly(
    MySchema,
    TSoftObjectPtr<UWorld>(LevelAsset),       // 可选关联关卡
    TSoftObjectPtr<UCineAssembly>(),           // 无父组装体
    Metadata,
    TEXT("/Game/Cinematic/Shots"),             // 创建路径
    TEXT("")                                    // 使用 Schema 默认命名
);
```

### 基本用法：管理 Production

```cpp
// 来源: Public/ProductionFunctionLibrary.h

// 获取所有可用的制作配置
TArray<FCinematicProduction> AllProductions = UProductionFunctionLibrary::GetAllProductions();

// 获取当前激活的制作
FCinematicProduction ActiveProduction;
bool bHasActive = UProductionFunctionLibrary::GetActiveProduction(ActiveProduction);

// 切换激活的制作
FGuid TargetProductionID = AllProductions[0].ProductionID;
UProductionFunctionLibrary::SetActiveProductionByID(TargetProductionID);

// 创建新的制作
FCinematicProduction NewProduction;
NewProduction.ProductionName = TEXT("MyFilm");
NewProduction.DefaultDisplayRate = FFrameRate(24, 1);
NewProduction.DefaultStartFrame = 0;
UProductionFunctionLibrary::AddProduction(NewProduction);
```

### 进阶用法：两阶段创建组装体（配置后持久化）

```cpp
// 来源: Public/CineAssemblyEditorFunctionLibrary.h
// 适用于需要在创建前修改组装体属性的场景

UCineAssemblySchema* Schema = LoadObject<UCineAssemblySchema>(nullptr, TEXT("/Game/Schema"));

// 第一阶段：创建内存中的临时组装体
UCineAssembly* TransientAssembly = UCineAssemblyEditorFunctionLibrary::CreateAssemblyToConfigure(
    Schema,
    TSoftObjectPtr<UWorld>(),
    TSoftObjectPtr<UCineAssembly>(),
    TMap<FString, FString>()
);

if (TransientAssembly)
{
    // 在此处修改临时组装体的属性...
    // 注意：不支持对临时对象调用 duplicate/rename/save API

    // 第二阶段：持久化为真实资产
    UCineAssembly* PersistedAssembly = UCineAssemblyEditorFunctionLibrary::FinalizeConfiguredAssembly(
        TransientAssembly,
        TEXT("/Game/Cinematic/Shots"),
        TEXT("")  // 使用已配置的名称
    );
}
```

### 进阶用法：注册 Production 扩展

```cpp
// 来源: Public/ICineAssemblyToolsEditorModule.h

// 定义自定义扩展数据结构
USTRUCT()
struct FMyProductionData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category=Default)
    FString CustomField;
};

// 在模块 StartupModule 中注册
void FMyModule::StartupModule()
{
    ICineAssemblyToolsEditorModule& CatModule = ICineAssemblyToolsEditorModule::Get();
    CatModule.RegisterProductionExtension(*FMyProductionData::StaticStruct());

    // 可选：自定义 Production Wizard 中的显示
    CatModule.RegisterProductionWizardCustomization(
        *FMyProductionData::StaticStruct(),
        FGetWidget(),                             // 使用默认 Details 视图
        FText::FromString(TEXT("Custom Data")),    // 自定义标签
        FSlateIcon(),                              // 自定义图标
        true,                                      // 显示 Production 选择器
        false                                      // 不隐藏
    );
}
```

### 进阶用法：安全修改 Production 扩展数据

```cpp
// 来源: Public/ScopedModifyProductionExtendedData.h

FCinematicProduction Production = UProductionFunctionLibrary::GetAllProductions()[0];

if (FInstancedStruct* Data = Production.FindOrLoadExtendedData(*FMyProductionData::StaticStruct()))
{
    // 使用作用域守卫确保修改后正确导出到配置
    FScopedModifyProductionExtendedData ModifyGuard(Production, *FMyProductionData::StaticStruct());

    FMyProductionData& MyData = Data->GetMutable<MyProductionData>();
    MyData.CustomField = TEXT("NewValue");

    // ModifyGuard 在作用域结束时自动调用 Finish()，将数据导出到配置
}
```

### 进阶用法：命名令牌求值

```cpp
// 来源: Public/CineAssemblyEditorFunctionLibrary.h

// 使用组装体上下文求值令牌字符串
FString TokenString = TEXT("{cat.schema}_{cat.shot}");
FNamingTokenResultData Result = UCineAssemblyEditorFunctionLibrary::EvaluateTokenString(
    TokenString,
    MyAssembly
);

// 获取求值后的文本
FString ResolvedText = Result.GetResolvedText();  // 例如: "MySchema_001"
```

## Demo 示例

### 最小示例：创建组装体并监听事件

```cpp
// MyCineAssemblyManager.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "MyCineAssemblyManager.generated.h"

UCLASS()
class UMyCineAssemblyManager : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 创建一个组装体并返回 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    class UCineAssembly* CreateDemoAssembly(const FString& ShotName);

private:
    FDelegateHandle OnAssemblyCreatedHandle;

    UFUNCTION()
    void OnAssemblyCreated(class UCineAssembly* NewAssembly);
};
```

```cpp
// MyCineAssemblyManager.cpp
#include "MyCineAssemblyManager.h"
#include "CineAssemblyEditorFunctionLibrary.h"
#include "CineAssemblyEditorSubsystem.h"

void UMyCineAssemblyManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 监听组装体创建事件
    if (UCineAssemblyEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UCineAssemblyEditorSubsystem>())
    {
        Subsystem->OnAssemblyCreated.AddDynamic(this, &UMyCineAssemblyManager::OnAssemblyCreated);
    }
}

void UMyCineAssemblyManager::Deinitialize()
{
    if (UCineAssemblyEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UCineAssemblyEditorSubsystem>())
    {
        Subsystem->OnAssemblyCreated.RemoveDynamic(this, &UMyCineAssemblyManager::OnAssemblyCreated);
    }

    Super::Deinitialize();
}

UCineAssembly* UMyCineAssemblyManager::CreateDemoAssembly(const FString& ShotName)
{
    // 加载 Schema
    UCineAssemblySchema* Schema = LoadObject<UCineAssemblySchema>(
        nullptr, TEXT("/Game/Cinematic/DemoSchema")
    );
    if (!Schema) return nullptr;

    // 准备元数据
    TMap<FString, FString> Metadata;
    Metadata.Add(TEXT("shot"), ShotName);

    // 创建组装体
    return UCineAssemblyEditorFunctionLibrary::CreateAssembly(
        Schema,
        TSoftObjectPtr<UWorld>(),          // 无关联关卡
        TSoftObjectPtr<UCineAssembly>(),   // 无父组装体
        Metadata,
        TEXT("/Game/Cinematic/DemoShots"),
        FString()                          // 使用 Schema 默认命名
    );
}

void UMyCineAssemblyManager::OnAssemblyCreated(UCineAssembly* NewAssembly)
{
    UE_LOG(LogTemp, Log, TEXT("Assembly created: %s"), *NewAssembly->GetName());
}
```

## 模块依赖

从 Build.cs 分析，以下为该插件的独特依赖（已省略标准 Core/Engine/Slate 依赖）：

| 模块 | 用途 |
|---|---|
| `MovieSceneTools` | Sequencer/MovieScene 核心工具，用于管理序列化场景结构和轨道 |
| `MovieScene` | MovieScene 核心运行时，用于操作轨道、Section、绑定等 |
| `LevelSequence` | LevelSequence 资产类型，CineAssembly 继承自此 |
| `LevelSequenceEditor` | Sequencer 编辑器集成，用于自定义轨道编辑器 |
| `NamingTokens` | 命名令牌系统，用于动态名称求值（如 `{cat.shot}`） |
| `SequencerWidgets` | Sequencer UI 组件 |
| `AssetDefinition` | 资产定义框架，用于自定义 CineAssembly 在内容浏览器中的显示 |
| `ToolMenus` | 工具菜单框架，用于扩展编辑器菜单和工具栏 |
| `ContentBrowser` | 内容浏览器集成 |
| `TakeRecorder` | Take Recorder 集成，用于录制工作流 |
| `TakeRecorderCore` | Take Recorder 核心运行时 |
| `TakeMetaData` | Take 元数据系统 |
| `DeveloperToolSettings` | 开发者工具设置 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `534c9605` | ShotManagement: Suppress warnings in output log when a CineAssemblySchema has no thumbnail brush ass | 抑制 Schema 无缩略图笔刷时的输出日志警告 |
| 2026-05-14 | `85850dc9` | ShotManagement: Add missing scripting API functions | 补充缺失的脚本 API 函数 |
| 2026-05-14 | `1d99acc3` | ShotManagement: Move ProductionFunctionLibrary.h into Public folder and add API exports | 将 ProductionFunctionLibrary 移入 Public 文件夹并添加 API 导出 |
| 2026-05-14 | `c11b4fd1` | ShotManagement: Add missing Cinematic Assembly Tools scripting API | 补充缺失的 CAT 脚本 API |
| 2026-05-14 | `d1ca5718` | ShotManagement: Remove non-ASCII characters from plugin files | 移除插件文件中的非 ASCII 字符 |

### 维护评价

**活跃维护中**。

- **创建时间**：2025-04-23，是一个非常新的插件（约 0 年）
- **近期更新**：最近一次更新集中在 2026-05-14，批量提交了多个 API 完善和兼容性修复，表明处于**活跃开发阶段**
- **状态**：标记为 `IsExperimentalVersion = true`，说明 Epic 认为该插件尚未达到稳定版本
- **API 完善度**：从最近的提交记录看，插件正在快速完善脚本 API（BlueprintCallable 函数），Public 头文件的 API 导出也在持续改进
- **规模**：104 个源文件，属于大型插件，包含丰富的 UI 组件和编辑器集成
- **首次提交说明**：从 `Shots` 插件重命名为 `CinematicAssemblyTools`，说明这是一个已有的内部工具的公开化/重命名
- **⚠️ 注意**：作为实验性插件，API 可能在版本间发生变化，建议关注更新日志

**推荐使用**：如果你的项目涉及虚拟制片或线性内容的镜头管理，且愿意接受实验性 API 的潜在变化，该插件提供了目前 UE5 中最完整的镜头管线工具集。建议在生产环境中使用前做好版本锁定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CinematicAssemblyTools)
- 官方文档：暂无（DocsURL 为空）
- 测试用例：插件目录内未发现独立测试文件