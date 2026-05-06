# Interchange OpenVDB

> Allows translation of OpenVDB files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | OpenVDB 互通翻译器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeOpenVDBImport` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-31 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenVDB) | |

## 用途

Interchange OpenVDB 是 Interchange 框架下的一个翻译器插件，用于将 OpenVDB 格式的体积数据（.vdb 文件）导入到 Unreal Engine 中。它实现了 `IInterchangeVolumePayloadInterface` 接口，利用 Interchange 的管线自动解析体积信息，生成体积资产（如稀疏体积纹理或体积缓存）。该插件当前作为实验性功能被隐藏（`Hidden: true`），主要用于内部测试和开发场景，不推荐普通项目直接使用。

## 使用场景

- 你想通过 Interchange 流程导入 OpenVDB 体积文件（如烟雾、火焰、云等程序化体积数据）
- 你在开发或测试 Interchange 框架，需要验证体积数据翻译能力
- 你已经手动启用了此插件，并配备了完整的 Interchange 依赖（通常用于引擎开发者调试）

> **注意**：由于插件被标记为隐藏且实验性，生产中建议优先使用官方其他体积导入方案（如 `VolumeTexture` 或 Houdini Engine 集成等）。

## 蓝图用法

插件本身不暴露新的蓝图节点，翻译器在后台自动运行。但你可以通过 Interchange 蓝图接口获取翻译结果：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSupportedFormats` | 返回支持的导入格式（`{"vdb;OpenVDB Volume"}`） | `UInterchangeOpenVDBTranslator` |
| `GetTranslatorType` | 返回翻译器类型（`EInterchangeTranslatorType::Scratch`） | `UInterchangeOpenVDBTranslator` |
| `GetSupportedAssetTypes` | 返回支持的资产类型（`EInterchangeTranslatorAssetType::Volume`） | `UInterchangeOpenVDBTranslator` |
| `CanImportSourceData` | 判断给定源数据是否可被翻译（检查扩展名等） | `UInterchangeOpenVDBTranslator` |

### 使用示例（蓝图描述）

1. 在 Content Browser 中右键导入 `.vdb` 文件（前提：已启用插件）
2. Interchange 自动根据扩展名匹配到 `UInterchangeOpenVDBTranslator`
3. 翻译器将文件解析为体积数据并通过 `IInterchangeVolumePayloadInterface` 生成资产
4. 最终生成体积资产（如 `VolumeTexture`）并放置在指定路径

由于插件被隐藏，蓝图无法直接引用翻译器类，所有交互通过 Interchange 系统自动完成。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeOpenVDBTranslator.h"
```

### 基本用法

通过 Interchange 框架注册翻译器，无需手动调用。当你使用 `FInterchangeImportExec` 或 `UInterchangeManager` 导入 `.vdb` 文件时，框架自动选取此翻译器：

```cpp
// 示例：触发 Interchange 导入（来自引擎测试）
UInterchangeManager& InterchangeManager = UInterchangeManager::GetInterchangeManager();
const FString FilePath = TEXT("/Game/TestData/volume.vdb");
bool bSuccess = InterchangeManager.ImportAsset(
    FilePath,
    GetTransientPackage(),
    TEXT("/Game/ImportedVolumes")
);
// 成功时，bSuccess 为 true，体积资产被创建
```

来源文件路径：`Engine/Plugins/Interchange/Extensions/OpenVDB/Source/Import/Private/InterchangeOpenVDBTranslator.cpp`

### 进阶用法

如果需要自定义翻译行为，可以继承 `UInterchangeOpenVDBTranslator` 并重写 `Translate` 或 `GetVolumePayloadData`。但通常直接使用默认实现。

```cpp
// 自定义翻译器（派生类）
UCLASS()
class UMyOpenVDBTranslator : public UInterchangeOpenVDBTranslator
{
    GENERATED_BODY()

public:
    virtual bool Translate(UInterchangeBaseNodeContainer& BaseNodeContainer) const override
    {
        // 前置处理...
        bool bBaseResult = Super::Translate(BaseNodeContainer);
        // 后置处理...
        return bBaseResult;
    }
};
```

> 注意：自定义翻译器需通过模块 Startup 注册到 Interchange 系统。

## Demo 示例

一个最小化示例，展示如何通过 C++ 使用 Interchange OpenVDB 翻译器导入 `.vdb` 文件（假设插件已启用）。

### MyActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InterchangeManager.h"
#include "MyActor.generated.h"

UCLASS()
class AMYPROJECT_API AMyActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Interchange")
    void ImportOpenVDB(const FString& FilePath, const FString& DestPackagePath);
};
```

### MyActor.cpp

```cpp
#include "MyActor.h"
#include "InterchangeManager.h"
#include "Engine/World.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    // 示例：导入文件
    ImportOpenVDB(TEXT("D:/Volumes/smoke.vdb"), TEXT("/Game/MyVolumes"));
}

void AMyActor::ImportOpenVDB(const FString& FilePath, const FString& DestPackagePath)
{
    UInterchangeManager& Manager = UInterchangeManager::GetInterchangeManager();
    FImportAssetParameters Params;
    Params.bIsAutomated = false;
    Params.ReimportSourceData = nullptr;

    bool bSuccess = Manager.ImportScene(
        FilePath,
        GetWorld()->GetPackage(),
        DestPackagePath,
        Params
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Interchange OpenVDB import succeeded."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Interchange OpenVDB import failed."));
    }
}
```

> 注意：需要确保 `Interchange` 和 `InterchangeOpenVDBImport` 模块已加载，且插件已启用。

## 模块依赖

以下模块是使用 `InterchangeOpenVDB` 时必须添加的依赖（在你的 `Build.cs` 中）。

| 模块 | 用途 |
|---|---|
| `Interchange` | 核心 Interchange 运行时，提供翻译管线和管理器 |
| `InterchangeCore` | Interchange 基础节点和数据结构 |
| `InterchangeVolume` | 体积数据载荷接口和设置类 |

其他标准依赖（Core, Engine, Slate 等）自动满足，无需显式列出。

## 维护状态

### 近期更新

| 日期 | Hash | Commit | 解读 |
|---|---|---|---|
| 2025-12-18 | `3f562d0e` | Fixed crash when Interchange stack names have been modified. | 修复因堆栈名称修改导致的崩溃 |
| 2025-05-01 | `07e44ca8` | [Interchange] UInterchangeBaseNode setup calls streamlining. | 优化基础节点设置流程 |
| 2025-04-11 | `28c2462e` | OpenVDB: Hide and disable the Interchange OpenVDB plugin for now, as it's only meant to be used by t | 暂时隐藏并禁用插件（仅供内部测试） |
| 2025-04-04 | `021af69a` | Interchange: Remove the "Support" suffixes from the OpenUSD and OpenVDB FriendlyNames | 移除友好名称中的“Support”后缀 |
| 2025-03-31 | `3c7c5c8a` | Interchange: Project setting for showing the reimport options dialog. | 初始创建 |

### 维护评价

- **创建时间**：2025-03-31，不足1年，属于非常新的插件。
- **近期更新**：最后一次积极提交在2025-12-18（修复崩溃），但在此之前有两次提交均为内部调整和插件隐藏。2025-04-11 明确将其隐藏并禁用，表明该插件当前不适合公开使用。
- **活跃状态**：自2025-12-18后约半年未更新（假设当前时间2025年中期），更新频率低。
- **已知问题**：插件被隐藏，需要手动修改 `.uplugin` 或配置文件才能启用。且文档指出“仅用于临时测试”。
- **推荐度**：**不推荐** 用于正式项目。建议使用官方其他 VDB 导入方案（如 Houdini Engine，或直接转换后通过 Volume Texture 导入）。若必须使用，需承担实验性插件稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenVDB)
- [Interchange 概述（官方文档）](https://docs.unrealengine.com/5.7/en-US/interchange-framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/Import/Interchange/OpenVDB)（推测路径，实际可能不存在）