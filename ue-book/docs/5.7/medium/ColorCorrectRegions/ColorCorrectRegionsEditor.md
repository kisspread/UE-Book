# Color Correction Regions (CCR)

> Color correction/shading constrained to regions/volumes

| 属性 | 值 |
|---|---|
| 中文名 | 色彩校正区域 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质实例） |
| 模块 | `ColorCorrectRegions` (Runtime), `ColorCorrectRegionsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-02-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ColorCorrectRegions) | |

## 用途

**Color Correction Regions (CCR)** 允许你使用区域/体积（如球体、盒体、圆柱体）来约束色彩校正效果，仅影响区域内的物体。它解决了传统全局后处理体积无法在场景中精确控制特定区域色彩的问题，常用于电影级光照调色、游戏关卡局部氛围调整或虚拟制片中的局部调色。

该插件将 `AColorCorrectRegion` Actor 放入场景，通过形状体积定义影响范围，并利用 Stencil 技术（结合 PostProcessInput）实现区域裁剪。它与引擎的 **Color Grading** 面板深度集成，支持实时编辑并即时预览效果，同时与 **Object Mixer** 协作以便于批量管理多个区域。

## 使用场景

- **电影/叙事场景**：对角色面部单独进行颜色校正，而不影响背景。
- **交互式关卡设计**：为特定房间或走廊创建冷暖对比色调。
- **虚拟制片**：现场实时调整布光色彩，仅作用于绿幕前的演员。
- **多区域调色**：同时放置多个区域，每个区域拥有独立的色温、饱和度、对比度等参数。

## 蓝图用法

由于 CCR 主要与编辑器 UI 和颜色分级后端交互，其核心功能在 **蓝图** 中主要体现为放置 Actor 和调整属性。以下列出通过蓝图可以访问的关键节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Actor from Class` (选择`AColorCorrectRegion`) | 在关卡中创建一个色彩校正区域 Actor | `UGameplayStatics` |
| `Region Type` | 设置区域形状（Sphere/Box/Cylinder） | `AColorCorrectRegion` |
| `Intensity` | 控制效果强度 (0~1) | `AColorCorrectRegion` |
| `Inner / Outer` | 定义区域内部与过渡范围 | `AColorCorrectRegion` |
| `Temperature` / `Tint` | 色温和色调调整 | `AColorCorrectRegion` |
| `Color Saturation` / `Contrast` / `Gamma` | 饱和度、对比度、伽马校正 | `AColorCorrectRegion` |
| `Enabled` | 激活/禁用该区域 | `AColorCorrectRegion` |
| `Priority` | 控制区域重叠时的优先级 | `AColorCorrectRegion` |

> **注意**：更多色彩校正属性（如 Lift, Gain, Offset）可通过细节面板或 **Color Grading** 面板访问。

### 使用示例（蓝图）

1. **放置一个球形区域**：在关卡蓝图中使用 `Spawn Actor from Class`，选择 `AColorCorrectRegion`。然后将返回的引用连接到 `Set Region Type`（设置为 Sphere），并设置 `Inner=500`, `Outer=1000`。
2. **实时调节色彩**：利用 `Get Actor of Class` 获取 CCR 实例，将其 `Temperature` 节点输出到滑块，通过用户输入动态改变色温。
3. **按优先级叠加**：对两个重叠区域分别设置 `Priority` 值（较高数值优先），使用 `Set Priority` 节点动态改变叠加顺序。

## C++ 用法

### 头文件引入

```cpp
#include "ColorCorrectRegions/Public/ColorCorrectRegions.h"   // 包含 AColorCorrectRegion 等核心类
#include "ColorCorrectRegionsEditor/Public/ColorCorrectRegionsEditorModule.h" // 编辑器模块
```

### 基本用法

创建一个颜色校正区域 Actor 并设置基本属性（参考测试用例 `ColorCorrectRegionsTest.cpp`）：

```cpp
// 在关卡中生成
AColorCorrectRegion* CCR = World->SpawnActorDeferred<AColorCorrectRegion>(
    AColorCorrectRegion::StaticClass(),
    FTransform::Identity,
    nullptr, nullptr,
    ESpawnActorCollisionHandlingMethod::AlwaysSpawn
);
if (CCR)
{
    CCR->RegionType = EColorCorrectRegionType::Sphere;
    CCR->Inner = 200.0f;
    CCR->Outer = 500.0f;
    CCR->Intensity = 0.8f;
    CCR->ColorGradingSettings.Temperature = 1500.0f;
    CCR->ColorGradingSettings.Saturation.Set(0.2f, 0.5f, 0.8f);
    CCR->FinishSpawning(FTransform(FVector(0.0f, 0.0f, 200.0f)));

    // 启用区域
    CCR->SetEnabled(true);
}
```

*来源：`Engine/Plugins/Experimental/ColorCorrectRegions/Source/ColorCorrectRegions/Private/ColorCorrectRegionsTest.cpp`（部分测试）*

### 进阶用法

利用 **Color Grading 数据模型** 在编辑器内自定义颜色分级面板的显示顺序：

```cpp
// 在模块 Startup 时注册自定义数据模型生成器
void FColorCorrectRegionsEditorModule::StartupModule()
{
    // 注册 Color Grading 数据模型生成器（为 CCR 提供专属分组）
    IColorGradingEditorDataModel::RegisterDataModelGenerator(
        AColorCorrectRegion::StaticClass(),
        FColorGradingDataModelGenerator_ColorCorrectRegion::MakeInstance
    );

    // 注册层级配置（支持 Object Mixer 拖拽）
    IColorGradingMixerObjectHierarchyConfig::RegisterHierarchyConfig(
        AColorCorrectRegion::StaticClass(),
        FColorGradingHierarchyConfig_ColorCorrectRegion::MakeInstance
    );

    // 自定义细节面板（隐藏无关属性）
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    PropertyModule.RegisterCustomClassLayout(
        AColorCorrectRegion::StaticClass()->GetFName(),
        FOnGetDetailCustomizationInstance::CreateStatic(&FColorCorrectWindowDetails::MakeInstance)
    );

    // 注册上下文菜单扩展
    ContextMenu->RegisterContextMenuExtender();
}
```

## Demo 示例

以下是一个最简单的 C++ 示例，演示如何在游戏启动时自动生成一个颜色校正区域，并将其绑定到 UI 滑块（假设有 Slate UI）：

**MyCCRDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ColorCorrectRegions/Public/ColorCorrectRegions.h"
#include "MyCCRDemo.generated.h"

UCLASS()
class AMyCCRDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="CCR Demo")
    AColorCorrectRegion* CCRInstance;

    UFUNCTION(BlueprintCallable, Category="CCR Demo")
    void UpdateIntensity(float NewIntensity);
};
```

**MyCCRDemo.cpp**
```cpp
#include "MyCCRDemo.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

void AMyCCRDemo::BeginPlay()
{
    Super::BeginPlay();

    // 在玩家位置生成一个盒体区域
    APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    if (PC && PC->GetPawn())
    {
        FTransform SpawnTransform(PC->GetPawn()->GetActorLocation() + FVector(0, 0, 100));
        CCRInstance = GetWorld()->SpawnActorDeferred<AColorCorrectRegion>(
            AColorCorrectRegion::StaticClass(),
            SpawnTransform
        );
        if (CCRInstance)
        {
            CCRInstance->RegionType = EColorCorrectRegionType::Box;
            CCRInstance->Inner = 300.0f;
            CCRInstance->Outer = 600.0f;
            CCRInstance->ColorGradingSettings.Temperature = -2000.0f; // 冷色
            CCRInstance->FinishSpawning(SpawnTransform);
            CCRInstance->SetEnabled(true);
        }
    }
}

void AMyCCRDemo::UpdateIntensity(float NewIntensity)
{
    if (CCRInstance)
    {
        CCRInstance->Intensity = FMath::Clamp(NewIntensity, 0.0f, 1.0f);
    }
}
```

## 模块依赖

使用此插件时，你的模块需要在 `Build.cs` 中添加以下依赖（省略常见依赖 Core, Engine, Slate 等）：

| 模块 | 用途 |
|---|---|
| `ColorCorrectRegions` | 提供核心 AColorCorrectRegion Actor 及运行时逻辑 |
| `ColorGrading` | 提供颜色分级编辑器数据模型和 UI 框架 |
| `ObjectMixer` | 提供对象混合器多选编辑支持 |
| `nDisplayModularFeatures` | 可选，用于 nDisplay 多屏投影环境中的区域同步 |

**编辑器模块（仅 Editor 目标）：**
- `ColorCorrectRegionsEditor`：提供细节面板、上下文菜单、样式等编辑器扩展。

## 维护状态

### 近期更新

- 2025-05-29 `f5ac91eb` 移除无效的 U 宏出现位置（代码清理）
- 2025-05-23 `994e1fc1` 限制区域视口到最大视口边界（修复状态问题）
- 2025-04-28 `ece68893` 仅在使用 CCR 时发出警告（减少误报）
- 2025-04-23 `394ea0ed` 增加无效模板设置的项目设置警告提示
- 2025-02-13 `ec3fb596` 替换 `IsValid(this)` 调用（引擎级重构）

### 维护评价

| 维度 | 评价 |
|---|---|
| **创建时间** | 2025-02-13，距今不足半年，属于全新插件 |
| **更新频率** | 活跃维护（近 3 个月有多次更新，涉及功能修复和引擎适配） |
| **内容质量** | 代码结构清晰，与 Color Grading 和 Object Mixer 深度集成 |
| **已知限制** | 区域裁剪依赖 Stencil 缓冲，可能与自定义 Stencil 冲突；性能受区域数量影响 |
| **推荐度** | ✅ 推荐用于需要局部色彩校正的影视/虚拟制片项目 |

**警告**：该插件仍在迭代中，API 可能发生微小变化。建议锁定版本并跟踪 Epic 更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ColorCorrectRegions)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/color-correction-regions-in-unreal-engine/)（截至 5.7，文档可能尚未发布，但可查阅英文页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/ColorCorrectRegions/Source/ColorCorrectRegions/Private/ColorCorrectRegionsTest.cpp)