# Text 3D

> Tool to create 3D Text with advanced options

| 属性 | 值 |
|---|---|
| 中文名 | 3D文本 |
| 分类 | Text |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `Text3D` (Runtime), `Text3DEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Text3D) | |

## 用途

Text3D 插件为 Unreal Engine 提供了一套完整的 3D 文本创建和管理解决方案。它解决了在引擎中生成可定制、高质量 3D 文本的基础需求，特别是为 Motion Design（动态设计）工作流提供支持。

与基础的文本渲染不同，此插件专注于：
1.  **真实的 3D 文本**：将文本转换为具有深度和几何体的 3D 网格。
2.  **高级字体支持**：集成了 FreeType 和 HarfBuzz 库，支持复杂的文本排版（如连字、双向文本）。
3.  **编辑器集成**：提供强大的编辑器工具，包括一个高级字体选择器，能够管理项目字体、系统字体，并支持收藏夹。
4.  **样式管理**：引入了 `UText3DStyleSet` 资产，允许用户预设和复用文本样式配置。
5.  **虚拟制作集成**：该插件从 Experimental 状态毕业并归类于 `VirtualProduction`，表明其成熟度和在虚拟制作流程中的适用性。

## 使用场景

-   **动态设计**：为电影、电视或广告创建动态的 3D 标题和字幕。
-   **游戏内 UI**：在游戏主菜单、加载界面或 HUD 中显示具有视觉冲击力的 3D 文本。
-   **建筑可视化**：在建筑漫游中添加带有真实光照和阴影的 3D 标注。
-   **品牌展示**：在虚拟场景中创建带有品牌标识的 3D 标牌。
-   **可定制文本**：任何需要用户运行时更改文本内容、字体、样式和对齐方式的场景。

## 蓝图用法

该插件主要通过 `UText3DComponent` 暴露蓝图功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Text` | 设置要显示的文本字符串 | `UText3DComponent` |
| `Set Font` | 设置文本使用的字体资产 | `UText3DComponent` |
| `Set Horizontal Alignment` | 设置文本的水平对齐方式（左、中、右） | `UText3DComponent` |
| `Set Vertical Alignment` | 设置文本的垂直对齐方式（上、中、下） | `UText3DComponent` |
| `Get Text` | 获取当前显示的文本 | `UText3DComponent` |
| `Get Font` | 获取当前使用的字体资产 | `UText3DComponent` |

### 使用示例（蓝图描述）

1.  **创建基础文本**：在你的 Actor 蓝图中，添加一个 `Text3DComponent`。在详细面板中，直接设置 `Text` 属性即可。
2.  **运行时更改文本**：获取对 `Text3DComponent` 的引用，然后使用 `Set Text` 节点连接一个字符串变量或函数返回值。
3.  **动态切换字体**：通过 `Set Font` 节点，将一个 `UFont*` 资产变量连接到字体输入引脚。这可以与编辑器中 `AdvancedFontPicker` 选择的字体联动。
4.  **调整对齐方式**：使用 `Set Horizontal Alignment` 或 `Set Vertical Alignment` 节点，连接 `EText3DHorizontalTextAlignment` 或 `EText3DVerticalTextAlignment` 枚举值。

## C++ 用法

### 头文件引入

```cpp
#include "Components/Text3DComponent.h"
```

### 基本用法

创建一个包含 3D 文本的 Actor。

```cpp
// MyText3DActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyText3DActor.generated.h"

class UText3DComponent;

UCLASS()
class AMyText3DActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyText3DActor();

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "3D Text")
	TObjectPtr<UText3DComponent> Text3DComponent;
};

// MyText3DActor.cpp
#include "MyText3DActor.h"
#include "Components/Text3DComponent.h"

AMyText3DActor::AMyText3DActor()
{
	PrimaryActorTick.bCanEverTick = false;

	Text3DComponent = CreateDefaultSubobject<UText3DComponent>(TEXT("Text3DComponent"));
	RootComponent = Text3DComponent;

	// 设置初始文本
	Text3DComponent->SetText(FText::FromString(TEXT("Hello, 3D Text!")));
}
```

*（基于常见 Actor 组件用法模式推断）*

### 进阶用法

动态创建并配置 3D 文本组件。

```cpp
void AMyActor::SpawnDynamic3DText(const FText& Text, UFont* Font, const FVector& Location)
{
    // 在指定位置生成一个包含 3D 文本的新 Actor
    FActorSpawnParameters SpawnParams;
    AActor* TextActor = GetWorld()->SpawnActor<AActor>(Location, FRotator::ZeroRotator, SpawnParams);
    
    if (TextActor)
    {
        // 动态创建组件
        UText3DComponent* TextComp = NewObject<UText3DComponent>(TextActor);
        TextComp->RegisterComponent();
        TextActor->SetRootComponent(TextComp);
        TextComp->SetWorldLocation(Location);
        
        // 配置文本属性
        TextComp->SetText(Text);
        if (Font)
        {
            TextComp->SetFont(Font);
        }
        TextComp->SetHorizontalAlignment(EText3DHorizontalTextAlignment::Center);
        TextComp->SetVerticalAlignment(EText3DVerticalTextAlignment::Center);
    }
}
```

*（基于 UText3DComponent 的公开 API 和组件创建逻辑推断）*

## Demo 示例

一个在游戏开始时创建并显示 3D 文本的 Actor。

**My3DTextDemoActor.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "GameFramework/Actor.h"
#include "My3DTextDemoActor.generated.h"

class UText3DComponent;

UCLASS(Blueprintable)
class AMy3DTextDemoActor : public AActor
{
	GENERATED_BODY()

public:
	AMy3DTextDemoActor();

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UText3DComponent> Text3DComponent;
};
```

**My3DTextDemoActor.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "My3DTextDemoActor.h"
#include "Components/Text3DComponent.h"

AMy3DTextDemoActor::AMy3DTextDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;

	// 创建 3D 文本组件
	Text3DComponent = CreateDefaultSubobject<UText3DComponent>(TEXT("DemoText"));
	RootComponent = Text3DComponent;
}

void AMy3DTextDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 在游戏开始时设置文本
	if (Text3DComponent)
	{
		Text3DComponent->SetText(FText::FromString(TEXT("Welcome to UE5 Text3D!")));
		// 注意：字体和对齐方式通常在构造函数或编辑器中设置更高效
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FreeType2` | 用于加载和栅格化字体文件（.ttf, .otf） |
| `HarfBuzz` | 用于复杂的文本整形和排版（处理连字、字形选择等） |
| `MeshMergeUtilities` | 用于合并生成的文本几何体网格 |
| `DirectX` | (Editor) 编辑器模块可能使用 DirectX 进行特定的渲染或计算 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `660d059d` | Text3D: Text3D relies on GeometryMask for its material functions (content-only dependency). As there | 将材质功能依赖转移至 GeometryMask 插件，清理了插件依赖关系。 |
| 2026-05-22 | `f3f717af` | Text3D: fix build errors when building with server (no free type) | 修复了在无 FreeType 库的服务器环境下构建时出现的错误。 |
| 2026-05-21 | `14da3adf` | Text3D: fixed issue where in the exact timing where preparation of Text3D only held onto new glyph h | 修复了一个与时序相关的问题，该问题导致字形准备过程中错误地持有句柄。 |
| 2026-05-15 | `2f367c6e` | Text3D: fix function defined in editor-only | 修复了一个仅在编辑器中定义的函数导致的编译问题。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，允许强制禁用 Text3D 和形状的碰撞。 |

### 维护评价

**积极维护中**。
-   **年龄**：该插件于 2025 年 9 月创建，非常“年轻”（约 1 年）。
-   **更新频率**：在 2026 年 5 月有一系列密集的修复和优化提交，表明其仍在被 Epic Games 活跃开发和维护。
-   **内容**：近期的更新集中在 bug 修复、依赖清理和增加新功能（碰撞设置），表明插件正走向稳定并完善功能。
-   **推荐**：**强烈推荐**。作为官方支持的、从 Experimental 成功毕业的 VirtualProduction 插件，它为 3D 文本需求提供了可靠且功能丰富的解决方案。鉴于其活跃的维护状态，可以放心在项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Text3D)
- [官方文档]() (暂无)
- [测试用例]() (源码中未提供测试文件路径)