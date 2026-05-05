# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、纹理等） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

MetaHuman Character 插件提供了一套完整的工具链，用于在 Unreal Engine 编辑器内创建、编辑和组装高保真数字人类（MetaHuman）角色资产。它不仅仅是导入工具，而是一个参数化的角色创作系统。用户可以通过调整面部特征、身体比例、皮肤纹理、眼睛、牙齿、化妆等数十个精细参数，从零开始或基于模板生成独一无二的角色。该插件的核心价值在于将复杂的数字人创建流程集成到引擎内部，实现了资产创建、编辑、预览和最终组装（Assembly）的一站式工作流，避免了对外部工具的依赖，并确保了资产与引擎渲染、动画系统的无缝兼容。

## 使用场景

- **游戏开发**：为你的游戏项目创建具有电影级质量的主角、NPC 或敌人角色，无需依赖昂贵的外包或扫描数据。
- **影视与虚拟制片**：快速生成和迭代数字替身或虚拟演员，用于实时渲染的虚拟制片场景。
- **建筑与设计可视化**：在建筑漫游或产品展示中添加逼真的人物，提升场景的真实感和沉浸感。
- **虚拟现实（VR）与增强现实（AR）**：创建用于社交VR或AR应用的个性化虚拟形象。
- **快速原型与概念验证**：在项目早期快速生成角色原型，用于测试动画、镜头或叙事。

## 蓝图用法

该插件的蓝图 API 主要围绕角色资产的配置和生成。核心数据结构（如 `FMetaHumanCharacterAssemblySettings`, `FMetaHumanCharacterViewportSettings`）均标记为 `BlueprintType`，允许在蓝图中直接创建和修改。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Assembly Settings` | 配置角色组装（Assembly）的管线类型、质量、输出目录等参数。 | `UMetaHumanCharacter` (通过子系统或资产编辑器访问) |
| `Set Viewport Settings` | 设置角色预览视口的环境、光照、LOD、相机帧等。 | `UMetaHumanCharacter` (通过子系统或资产编辑器访问) |
| `Set Skin Properties` | 调整角色皮肤的色调、粗糙度、纹理索引等属性。 | `UMetaHumanCharacter` (通过子系统或资产编辑器访问) |
| `Set Eye Properties` | 修改眼睛的虹膜图案、颜色、阴影、巩膜环等细节。 | `UMetaHumanCharacter` (通过子系统或资产编辑器访问) |
| `Set Teeth Properties` | 控制牙齿的长度、间距、颜色、磨损程度等。 | `UMetaHumanCharacter` (通过子系统或资产编辑器访问) |
| `Set Makeup Properties` | 应用和调整粉底、眼妆、唇妆等化妆效果。 | `UMetaHumanCharacter` (通过子系统或资产编辑器访问) |
| `Try Generate Character Assets` | 触发根据当前参数生成最终的角色网格体、材质、纹理等资产。 | `UMetaHumanCharacterEditorSubsystem` |

### 使用示例（蓝图描述）

1.  **创建角色资产**：在内容浏览器中右键，选择 `MetaHuman > MetaHuman Character` 创建一个新的 `UMetaHumanCharacter` 资产。
2.  **编辑角色**：双击打开资产，进入专用的角色编辑器。在编辑器的细节面板中，你可以找到所有可调参数（如 `Face`, `Body`, `Skin`, `Eyes` 等分类）。
3.  **蓝图控制**：在关卡蓝图或任何其他蓝图中，你可以通过 `MetaHuman Character Editor Subsystem` 获取对角色资产的引用，并调用上述节点来程序化地修改角色属性。
4.  **生成资产**：在编辑器中点击“生成”按钮，或在蓝图中调用 `Try Generate Character Assets`，插件会根据当前设置生成完整的 Skeletal Mesh、材质实例和纹理，并保存到指定的目录中。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCharacter.h"
#include "MetaHumanCharacterAssemblySettings.h"
#include "MetaHumanCharacterViewport.h"
// 根据需要引入其他具体属性的头文件，如 MetaHumanCharacterSkin.h, MetaHumanCharacterEyes.h 等
```

### 基本用法

以下代码展示了如何在 C++ 中创建一个 `MetaHumanCharacter` 资产并修改其组装设置。

```cpp
// 假设在某个编辑器工具或子系统中
#include "MetaHumanCharacter.h"
#include "MetaHumanCharacterAssemblySettings.h"
#include "AssetRegistry/AssetRegistryModule.h"

void CreateAndConfigureMetaHumanCharacter()
{
    // 1. 创建资产
    UPackage* Package = CreatePackage(TEXT("/Game/MyMetaHumans/MyNewCharacter"));
    UMetaHumanCharacter* NewCharacter = NewObject<UMetaHumanCharacter>(Package, TEXT("MyNewCharacter"), RF_Public | RF_Standalone);
    
    // 2. 修改组装设置
    FMetaHumanCharacterAssemblySettings AssemblySettings;
    AssemblySettings.PipelineType = EMetaHumanDefaultPipelineType::Optimized; // 使用优化管线
    AssemblySettings.PipelineQuality = EMetaHumanQualityLevel::Medium; // 设置中等质量
    AssemblySettings.RootDirectory.Path = TEXT("/Game/MyMetaHumans/Generated");
    // 将设置应用到角色资产 (假设存在一个设置方法，具体API需查阅完整头文件)
    // NewCharacter->SetAssemblySettings(AssemblySettings);
    
    // 3. 标记资产为已修改并保存
    NewCharacter->MarkPackageDirty();
    FAssetRegistryModule::AssetCreated(NewCharacter);
    Package->SavePackage();
}
```

### 进阶用法

结合视口设置和皮肤属性进行更精细的控制。

```cpp
#include "MetaHumanCharacterViewport.h"
#include "MetaHumanCharacterSkin.h"

void CustomizeCharacterAppearance(UMetaHumanCharacter* Character)
{
    if (!Character) return;
    
    // 修改视口设置以在特定环境下预览
    FMetaHumanCharacterViewportSettings ViewportSettings;
    ViewportSettings.CharacterEnvironment = EMetaHumanCharacterEnvironment::Moonlight;
    ViewportSettings.LevelOfDetail = EMetaHumanCharacterLOD::LOD2;
    ViewportSettings.RenderingQuality = EMetaHumanCharacterRenderingQuality::High;
    // Character->SetViewportSettings(ViewportSettings);
    
    // 调整皮肤属性
    FMetaHumanCharacterSkinProperties SkinProperties;
    SkinProperties.U = 0.7f; // 调整肤色U坐标
    SkinProperties.V = 0.3f; // 调整肤色V坐标
    SkinProperties.Roughness = 1.1f; // 增加皮肤粗糙度
    SkinProperties.BodyTextureIndex = 3; // 选择第4个身体纹理
    // Character->SetSkinProperties(SkinProperties);
    
    // 注意：实际的设置函数名可能为 Set*Properties 或直接访问成员，需根据完整API确定。
    // 通常，这些属性是 UPROPERTY，可以通过反射或直接访问进行修改。
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个 MetaHuman 角色资产并修改其牙齿属性。

**MyMetaHumanTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyMetaHumanTool.generated.h"

class UMetaHumanCharacter;

UCLASS()
class UMyMetaHumanTool : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman Tool")
    void CreateCharacterWithCustomTeeth();
};
```

**MyMetaHumanTool.cpp**
```cpp
#include "MyMetaHumanTool.h"
#include "MetaHumanCharacter.h"
#include "MetaHumanCharacterTeeth.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "UObject/SavePackage.h"

void UMyMetaHumanTool::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UMyMetaHumanTool::Deinitialize()
{
    Super::Deinitialize();
}

void UMyMetaHumanTool::CreateCharacterWithCustomTeeth()
{
    // 创建包和资产
    const FString AssetPath = TEXT("/Game/MyMetaHumans/CharacterWithCustomTeeth");
    UPackage* Package = CreatePackage(*AssetPath);
    UMetaHumanCharacter* Character = NewObject<UMetaHumanCharacter>(Package, TEXT("CharacterWithCustomTeeth"), RF_Public | RF_Standalone);

    // 配置牙齿属性
    FMetaHumanCharacterTeethProperties TeethProps;
    TeethProps.ToothLength = 0.2f; // 稍微加长牙齿
    TeethProps.ToothSpacing = -0.1f; // 减少牙齿间距
    TeethProps.TeethColor = FLinearColor(0.95f, 0.95f, 0.9f, 1.0f); // 微黄的牙齿颜色
    TeethProps.WornDown = 0.3f; // 添加一些磨损效果
    TeethProps.RecedingGums = 0.1f; // 轻微的牙龈萎缩

    // 将牙齿属性应用到角色 (假设存在直接设置方法)
    // Character->SetTeethProperties(TeethProps);
    // 注意：实际API可能需要通过编辑器子系统或直接修改成员变量。

    // 保存资产
    Character->MarkPackageDirty();
    FAssetRegistryModule::AssetCreated(Character);
    Package->SavePackage();

    UE_LOG(LogTemp, Log, TEXT("MetaHuman character with custom teeth created at: %s"), *AssetPath);
}
```

## 模块依赖

从模块名称和常见 MetaHuman 插件架构推断，使用此插件可能需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供 MetaHuman 系统的核心类型、接口和基础功能。 |
| `MetaHumanSDK` | MetaHuman 的软件开发工具包，可能包含模型、管线等底层逻辑。 |
| `MetaHumanIdentity` | 用于处理 MetaHuman 身份资产和面部识别相关功能。 |
| `MetaHumanProjectUtilities` | 提供项目级别的工具和设置，如默认管线配置。 |
| `RigLogic` | 用于驱动 MetaHuman 面部和身体动画的 RigLogic 运行时。 |
| `ChaosCloth` | 用于模拟 MetaHuman 角色衣物的布料解算系统。 |

*注：具体依赖需以各模块的 `Build.cs` 文件为准。*

## 维护状态

### 近期更新

```
- 2025-10-03 119e3b89c1c9 [UEMHC] 修复当覆盖的身体纹理不在项目中或无法加载时导致的崩溃
- 2025-09-15 9b20a0d5b79d [UEMHC] 组装导出目录字段默认显示为空白
- 2025-08-20 88bab4c7ac3a [UEMHC] 来自 BugHawk 和 PVS 的一些小修复
```

### 维护评价

- **创建时间**：插件创建于 2025 年 3 月，非常年轻。
- **最近更新**：最近一次更新在 2025 年 10 月，距今不足 1 个月，更新频率较高，且内容为功能修复和优化，表明处于**活跃开发**阶段。
- **维护状态**：**活跃维护中**。作为 Epic Games 官方维护的 MetaHuman 工具链核心部分，预计会持续更新以支持新引擎版本和功能。
- **已知限制**：插件标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，意味着它仍处于测试阶段，可能存在未发现的 Bug 或 API 变动，不建议在追求绝对稳定的生产环境中直接使用。
- **推荐使用**：对于希望在 UE 内部创建和编辑 MetaHuman 角色的项目，尤其是在原型开发、独立游戏或对工作流集成度要求高的场景，**强烈推荐使用**。但需注意其 Beta 状态，并做好应对潜在问题的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [官方文档]() (暂无)
- [测试用例]() (暂无)