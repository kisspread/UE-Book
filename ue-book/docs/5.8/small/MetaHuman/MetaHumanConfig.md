# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图工具、编辑器扩展） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 约 2022 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个综合性的工具链插件，用于驱动和处理 MetaHuman 角色的动画数据。它解决的核心问题是**将现实世界中的人脸表演数据（如视频、深度、控制点）高效、准确地转换为可用于 MetaHuman 角色的动画**。它不仅仅是一个简单的播放器，而是一个包含数据捕获、面部追踪、动画求解、性能优化和编辑器集成的完整管线。

该插件的存在是为了提供一个端到端的解决方案，让开发者能够方便地将演员的表演赋予虚拟的 MetaHuman 角色，实现高质量的面部动画，而无需离开 Unreal Engine 环境。

## 使用场景

-   **影视与虚拟制片**：你需要将演员在绿幕前的面部表演实时或离线驱动到现场的 MetaHuman 角色上，用于虚拟制片（Virtual Production）的预览或最终输出。
-   **游戏开发**：你希望为游戏中的 MetaHuman NPC 或主角制作大量基于真人表演的、高质量的面部动画，而不是从头手动制作。
-   **内容创作与预演**：你使用 iPhone 或专业深度摄像头捕获了面部数据，需要将其转化为可用的动画序列，用于动画预演（Previz）或短视频创作。
-   **语音驱动动画**：你有一个音频文件，希望为其生成对应的面部动画（Speech2Face），用于有声读物、快速原型制作等场景。
-   **批量处理**：你拥有大量的面部捕获数据，需要通过批处理功能（`MetaHumanBatchProcessor`）自动将其转化为动画，以提高工作流效率。

## 蓝图用法

本插件的核心交互逻辑主要集中在编辑器和内容管线中，但为运行时集成和配置提供了一些蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReadFromDirectory` | 从指定目录读取加密的配置数据并填充到当前配置资产中。是初始化配置资产的关键蓝图节点。 | `UMetaHumanConfig` |

### 使用示例（蓝图描述）

在蓝图中，你通常会操作 `MetaHuman Config` 资产。例如，你可以创建一个新的 `MetaHumanConfig` 资产变量，然后调用其 `ReadFromDirectory` 函数，传入包含求解器或拟合配置数据的文件夹路径。函数执行成功后，该资产将被填充数据，你可以通过其属性（如 `Type`、`Name`）查看配置信息，但具体的内部数据（如 `SolverTemplateData`）无法在蓝图中直接访问，供其他 C++ 模块或工具在引擎内部使用。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanConfig.h"
```

### 基本用法

`MetaHumanConfig` 模块的核心是 `UMetaHumanConfig` 资产类。以下代码演示了如何在 C++ 中程序化地创建和加载一个配置资产。
（来源：基于 `UMetaHumanConfig` 类定义推断的典型用法）

```cpp
// 在某个函数或类中
UCLASS()
class UMyAssetManager : public UObject
{
    GENERATED_BODY()

public:
    // 创建并加载一个配置资产
    UMetaHumanConfig* LoadConfigFromDisk(const FString& ConfigDirectory)
    {
        // 创建一个新的配置资产对象
        UMetaHumanConfig* ConfigAsset = NewObject<UMetaHumanConfig>();
        if (ConfigAsset)
        {
            // 从目录读取加密数据
            bool bSuccess = ConfigAsset->ReadFromDirectory(ConfigDirectory);
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("成功加载配置， 类型: %d, 名称: %s"),
                    static_cast<int32>(ConfigAsset->Type), *ConfigAsset->Name);
                return ConfigAsset;
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("从目录加载配置失败: %s"), *ConfigDirectory);
            }
        }
        return nullptr;
    }

    // 使用配置中的求解器数据
    void InitializeFaceSolver(const UMetaHumanConfig* SolverConfig)
    {
        if (!SolverConfig)
        {
            return;
        }

        // 检查配置类型
        if (SolverConfig->Type == EMetaHumanConfigType::Solver)
        {
            // 获取求解器模板和配置数据（内部会自动解密）
            FString TemplateData = SolverConfig->GetSolverTemplateData();
            FString ConfigData = SolverConfig->GetSolverConfigData();

            // ... 使用 TemplateData 和 ConfigData 初始化面部求解器 (MetaHumanFaceFittingSolver) ...
        }
        else if (SolverConfig->Type == EMetaHumanConfigType::PredictiveSolver)
        {
            // 获取预测求解器的训练数据
            TArray<uint8> TrainingData = SolverConfig->GetPredictiveTrainingData();
            // ... 使用训练数据初始化预测求解器 (MetaHumanFaceAnimationSolver) ...
        }
    }
};
```

### 进阶用法

更复杂的场景可能涉及验证配置的有效性，或者处理不同类型的配置组合。`UMetaHumanConfig` 内部提供了 `VerifySolverConfig` 和 `VerifyFittingConfig` 等私有验证方法，通常在 `ReadFromDirectory` 流程中被调用。开发者也可以参考其验证逻辑来确保传入的数据格式正确。

```cpp
// 示例：检查已加载配置的完整性
bool CheckConfigIntegrity(const UMetaHumanConfig* ConfigToCheck)
{
    if (!ConfigToCheck) return false;

    // 这个过程类似于 UMetaHumanConfig::ReadFromDirectory 内部的验证
    // 实际验证由私有方法完成，此处展示其逻辑
    if (ConfigToCheck->Type == EMetaHumanConfigType::Fitting)
    {
        // 尝试解密所有拟合相关的数据字段
        FString FittingTemplate = ConfigToCheck->GetFittingTemplateData();
        FString FittingConfig = ConfigToCheck->GetFittingConfigData();
        FString FittingTeeth = ConfigToCheck->GetFittingConfigTeethData();
        // ... 获取其他拟合数据 ...

        // 如果任何一个字段解密失败或为空，说明配置文件可能损坏
        if (FittingTemplate.IsEmpty() || FittingConfig.IsEmpty())
        {
            UE_LOG(LogMetaHumanConfig, Error, TEXT("拟合配置数据完整性检查失败"));
            return false;
        }
        return true;
    }
    // ... 检查其他类型 ...
    return false;
}
```

## Demo 示例

以下是一个完整的最小示例，展示了如何创建一个 `MetaHumanConfig` 资产并从文件系统读取数据。

**MyMetaHumanConfigManager.h**
```cpp
// MyMetaHumanConfigManager.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanConfigManager.generated.h"

class UMetaHumanConfig;

UCLASS(BlueprintType, Blueprintable)
class MYPROJECT_API UMyMetaHumanConfigManager : public UObject
{
    GENERATED_BODY()

public:
    /**
     * 从指定的文件夹路径加载一个 MetaHuman 配置资产。
     * @param InConfigFolderPath 包含配置文件的文件夹路径。
     * @return 成功加载的配置资产对象，失败则返回 nullptr。
     */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Config")
    UMetaHumanConfig* LoadMetaHumanConfig(const FString& InConfigFolderPath);

    /**
     * 获取配置资产中存储的求解器模板数据（已解密）。
     * @param InConfig 已加载的配置资产。
     * @return 求解器模板数据的 JSON 字符串，如果配置类型不匹配或数据无效则返回空。
     */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Config")
    FString GetSolverTemplateFromConfig(UMetaHumanConfig* InConfig);
};
```

**MyMetaHumanConfigManager.cpp**
```cpp
// MyMetaHumanConfigManager.cpp
#include "MyMetaHumanConfigManager.h"
#include "MetaHumanConfig.h"

UMetaHumanConfig* UMyMetaHumanConfigManager::LoadMetaHumanConfig(const FString& InConfigFolderPath)
{
    if (InConfigFolderPath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("LoadMetaHumanConfig: 提供的路径为空"));
        return nullptr;
    }

    UMetaHumanConfig* NewConfig = NewObject<UMetaHumanConfig>();
    if (NewConfig)
    {
        if (NewConfig->ReadFromDirectory(InConfigFolderPath))
        {
            UE_LOG(LogTemp, Log, TEXT("成功从路径 '%s' 加载 MetaHuman 配置"), *InConfigFolderPath);
            return NewConfig;
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("从路径 '%s' 加载 MetaHuman 配置失败"), *InConfigFolderPath);
            // 可以选择在这里销毁失败的对象
            // NewConfig->ConditionalBeginDestroy();
            return nullptr;
        }
    }
    return nullptr;
}

FString UMyMetaHumanConfigManager::GetSolverTemplateFromConfig(UMetaHumanConfig* InConfig)
{
    if (!InConfig)
    {
        UE_LOG(LogTemp, Warning, TEXT("GetSolverTemplateFromConfig: 提供的配置对象为空"));
        return FString();
    }

    // 检查配置类型是否为求解器类型
    if (InConfig->Type == EMetaHumanConfigType::Solver)
    {
        // 调用函数获取数据，此函数内部会处理解密
        return InConfig->GetSolverTemplateData();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("GetSolverTemplateFromConfig: 配置类型 (EMetaHumanConfigType::%d) 不是求解器类型"),
            static_cast<int32>(InConfig->Type));
        return FString();
    }
}
```

## 模块依赖

`MetaHumanConfig` 模块的依赖非常集中。要使用它，你的模块需要链接以下独特的模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供底层的核心技术库支持，可能是加密、解密和算法验证等功能的实现基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当身体追踪启用时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 身体的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象，避免干扰。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer（序列器）的缓存问题。 |

### 维护评价

MetaHuman Animator 是 Epic Games 的官方旗舰动画工具链之一，创建时间较新（约3年），且从 Git 提交记录来看，**维护非常活跃**。最近一周内有多次针对动画导出、渲染和缓存等问题的修复与功能优化。作为 MetaHuman 生态系统的核心驱动插件，它持续得到 Epic 的投入，功能不断完善和稳定。

**推荐使用**：如果你的项目需要基于性能捕捉或语音驱动的 MetaHuman 角色动画，此插件是官方且推荐的解决方案。需要注意的是，它是一个功能复杂、模块众多的大型插件，需要一定的学习成本。由于 `IsBetaVersion=false`，它已处于正式发布状态，可以用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （暂无）
- [测试用例]() （源码中包含测试模块，如 `MetaHumanControlsConversionTest`，但路径未提供）