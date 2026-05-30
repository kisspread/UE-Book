# AvalancheText

> 3D 文本处理模块，为 Motion Design 提供字体管理、材质桥接和文本组件扩展功能。

| 属性 | 值 |
|---|---|
| 中文名 | 文本处理 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheText` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheText) | |

## 用途

`AvalancheText` 是 Motion Design 插件的核心文本模块。它**不是**一个独立的插件，而是 Motion Design 的一部分，专门负责在虚拟制作工作流中创建、管理和渲染 3D 文本。其核心功能包括：

1.  **字体系统**：提供 `FAvaFont` 结构体和 `UAvaFontObject` 资产，用于管理字体（系统字体、项目字体），支持收藏、回退到默认字体、序列化缺失检测等高级功能。
2.  **3D 文本组件**：扩展了引擎自带的 `UText3DComponent`，创建了 `UAvaText3DComponent`，用于在 Motion Design 环境中承载 3D 文本。
3.  **材质桥接**：通过一系列 `Material Bridge` 类（如 `FText3DComponentMaterialBridge`， `FText3DDefaultExtensionMaterialBridge`），为 3D 文本组件及其材质扩展（如 `UText3DMaterialExtensionBase`）提供统一的材质状态访问、存储和应用接口，便于实现复杂的材质动态效果和状态管理。
4.  **遗留支持**：包含已废弃的 `AAvaTextActor` 和相关属性，以支持旧版资产。

该模块解决了在专业广播和动态图形制作中，对 3D 文本进行精细化、可编程控制的需求，是 Motion Design 工具链的基石。

## 使用场景

- 你在制作电视节目包装或虚拟演播室，需要动态生成、变换带有自定义材质的 3D 标题文字。
- 你需要一个统一的系统来管理项目中所有 3D 文本使用的字体，并支持从系统字体列表或项目资产中选择。
- 你希望为 3D 文本的各个部分（前表面、侧面、斜角）独立控制材质，并能够轻松保存和恢复复杂的材质状态。
- 你在使用 Motion Design 的其他功能（如克隆器、效果器、过渡动画）时，需要一个标准化的组件接口来操控文本属性。

## 蓝图用法

本模块提供的核心蓝图功能主要围绕字体数据结构的查询和操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Font` | 获取当前 `FAvaFont` 引用的 `UFont` 对象，若无效则返回默认字体。 | `FAvaFont` |
| `Get Font Name` | 获取当前字体的名称（FString）。 | `FAvaFont` |
| `Is Default Font` | 检查当前字体是否为默认字体。 | `FAvaFont` |
| `Is Fallback Font` | 检查当前字体是否处于回退状态（即引用的字体资产丢失）。 | `FAvaFont` |
| `Is Monospaced` | 检查当前字体是否为等宽字体。 | `FAvaFont` |
| `Is Bold` | 检查当前字体是否为粗体。 | `FAvaFont` |
| `Is Italic` | 检查当前字体是否为斜体。 | `FAvaFont` |
| `Get Font` | 从 `UAvaFontObject` 获取其持有的 `UFont`。 | `UAvaFontObject` |
| `Get Font Name` | 从 `UAvaFontObject` 获取字体名称。 | `UAvaFontObject` |
| `Get Source` | 获取字体的来源（系统、项目或无效）。 | `UAvaFontObject` |
| `Set Color Data` | 设置 `AAvaTextActor` 的颜色数据。 | `AAvaTextActor` |
| `Get Color Data` | 获取 `AAvaTextActor` 的颜色数据。 | `AAvaTextActor` |

### 使用示例（蓝图描述）

1.  **检查文本字体状态**：
    - 创建一个 `FAvaFont` 变量（通常通过组件属性获取）。
    - 将该变量拖入图表，连接到 `Get Font` 节点，即可得到 `UFont` 引用，可直接用于其他需要字体的节点。
    - 连接 `Is Fallback Font` 节点，用于判断资产加载是否正常，并据此给用户提示。

2.  **枚举和比较字体**：
    - 在文本处理逻辑中，可能需要比较两个 `FAvaFont` 是否相同。
    - 将两个 `FAvaFont` 变量分别拖入图表，使用 `==` 运算符节点进行比较，根据结果分支执行不同逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "Font/AvaFont.h"
#include "Font/AvaFontObject.h"
#include "AvaText3DComponent.h"
```

### 基本用法

以下代码展示了如何使用 `FAvaFont` 来获取和管理字体。

```cpp
// 来源: Public/Font/AvaFont.h

// 1. 创建一个默认的 FAvaFont 实例
FAvaFont MyFont;

// 2. 获取实际的 UFont 指针（保证有效，默认字体为 Roboto）
UFont* ActualFont = MyFont.GetFont();

// 3. 检查字体属性
if (MyFont.IsMonospaced())
{
    UE_LOG(LogTemp, Log, TEXT("当前字体是等宽字体。"));
}

if (MyFont.IsFallbackFont())
{
    UE_LOG(LogTemp, Warning, TEXT("字体资产丢失，已使用默认字体替代。"));
    // 可以进一步获取丢失字体的名字
    const FString& MissingName = MyFont.GetMissingFontName();
    UE_LOG(LogTemp, Warning, TEXT("丢失的字体名: %s"), *MissingName);
}

// 4. 将字体标记为收藏
MyFont.SetFavorite(true);
```

### 进阶用法

结合 `UAvaFontObject` 和序列化，进行更复杂的字体管理。

```cpp
// 来源: Public/Font/AvaFontObject.h, Public/Font/AvaFont.h

// 1. 通过字体对象初始化 FAvaFont
UAvaFontObject* FontObject = NewObject<UAvaFontObject>();
// ... 初始化 FontObject，例如加载一个项目字体 ...
FAvaFont ProjectFont(FontObject);

// 2. 检查字体来源
EAvaFontSource Source = ProjectFont.GetFontSource();
switch (Source)
{
case EAvaFontSource::System:
    UE_LOG(LogTemp, Log, TEXT("这是一个系统字体。"));
    break;
case EAvaFontSource::Project:
    UE_LOG(LogTemp, Log, TEXT("这是一个项目内字体。"));
    break;
case EAvaFontSource::Invalid:
    UE_LOG(LogTemp, Warning, TEXT("字体对象无效。"));
    break;
}

// 3. 生成格式化字符串（用于批量属性设置等场景）
FString FormattedString;
if (FAvaFont::GenerateFontFormattedString(FontObject, FormattedString))
{
    UE_LOG(LogTemp, Log, TEXT("字体格式化字符串: %s"), *FormattedString);
}
```

## Demo 示例

下面是一个简单的组件示例，展示如何创建一个 3D 文本生成器，并应用自定义字体。

**AvaTextGeneratorComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Font/AvaFont.h"
#include "AvaText3DComponent.h"
#include "AvaTextGeneratorComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UAvaTextGeneratorComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UAvaTextGeneratorComponent();

protected:
    virtual void BeginPlay() override;

public:
    /** 用于生成文本的模板字符串 */
    UPROPERTY(EditAnywhere, Category = "Text Generator")
    FString TextTemplate = TEXT("Hello, Motion Design! %d");

    /** 应用的字体 */
    UPROPERTY(EditAnywhere, Category = "Text Generator")
    FAvaFont TextFont;

    /** 文本组件引用 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Text Generator")
    TObjectPtr<UAvaText3DComponent> TextComponent;

private:
    void GenerateText();
};
```

**AvaTextGeneratorComponent.cpp**
```cpp
#include "AvaTextGeneratorComponent.h"
#include "Font/AvaFont.h" // 为获取 GetDefaultFont
#include "Engine/Font.h"

UAvaTextGeneratorComponent::UAvaTextGeneratorComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    TextComponent = CreateDefaultSubobject<UAvaText3DComponent>(TEXT("GeneratedText"));
}

void UAvaTextGeneratorComponent::BeginPlay()
{
    Super::BeginPlay();
    GenerateText();
}

void UAvaTextGeneratorComponent::GenerateText()
{
    // 检查字体是否有效，如果无效则使用默认字体
    UFont* FontToUse = TextFont.GetFont(); // 内部会处理回退到默认字体
    if (!FontToUse)
    {
        // 极端情况下的备用方案
        FontToUse = FAvaFont::GetDefaultFont();
    }

    // 应用字体到文本组件（假设 UText3DComponent 有相关设置方法）
    // TextComponent->SetFont(FontToUse); // 具体API需参考 UText3DComponent

    // 格式化文本
    int32 Counter = 0;
    FString FinalText = FString::Printf(*TextTemplate, Counter);

    // 设置文本内容（具体API需参考 UText3DComponent）
    // TextComponent->SetText(FinalText);

    UE_LOG(LogTemp, Log, TEXT("已生成文本: %s， 使用字体: %s"),
        *FinalText,
        FontToUse ? *FontToUse->GetName() : TEXT("None"));
}
```

## 模块依赖

`AvalancheText` 模块依赖多个其他模块来提供完整功能。

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | Motion Design 的核心基础模块 |
| `Text3D` | 引擎的 3D 文本组件基础 |
| `Material` | 材质系统基础 |
| `Slate`, `SlateCore` | 用于编辑器UI和字体预览 |
| `Avalanche` | Motion Design 的主模块 |

（注：`Core`, `CoreUObject`, `Engine`, `Projects` 等常见依赖已省略）

## 维护状态

该模块作为 Motion Design 插件的一部分，由 Epic Games 团队持续维护，是虚拟制作工具链中的活跃组件。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的选项卡（场景设置、大纲）移动到编辑器自己的分组中。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用“节目单页面”设置时添加了 MRQ 分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加了页面加载选项（全部、下一个、选中），并添加了... |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 通过在客户端关联或解除关联时进行通知，优化了视口中的强制性代码复制。 |

### 维护评价

- **活跃维护**：最近半年内有持续的功能性提交，主要集中在工作流优化、分析工具集成和编辑器体验改进上。
- **核心组件**：作为 Motion Design 的文本核心，其稳定性和功能性对整个插件至关重要。
- **推荐使用**：如果你在项目中使用 Motion Design 进行动态图形或虚拟制作，那么 `AvalancheText` 是创建和操控 3D 文本的**唯一且必需**的模块。它的设计考虑了专业广播工作流的需求（如材质管理、字体状态跟踪），并持续得到更新。不使用 Motion Design 的纯 C++ 或蓝图项目通常不需要直接依赖此模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheText)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/) (Motion Design 总体文档，包含文本相关内容)