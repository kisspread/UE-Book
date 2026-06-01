# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无（纯代码插件） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 文档结构

本插件规模为 **xlarge**（2060 源文件，43 个模块），按子模块拆分文档：

| 模块 | 说明 | 文档 |
|---|---|---|
| AvalancheText | 3D 文本组件、字体管理、材质桥接 | [AvalancheText](#avatext-子模块)（本文档） |
| AvalancheCamera | 摄像机系统 | 待补充 |
| AvalancheEffectors / ClonerEffector | 效果器和克隆系统 | 待补充 |
| AvalancheMaterial | 动态材质设计 | 待补充 |
| AvalancheMedia | 媒体合成和广播 | 待补充 |
| AvalancheModifiers | Actor 修改器 | 待补充 |
| AvalancheSequencer | Sequencer 集成 | 待补充 |
| AvalancheShapes | 几何形状 | 待补充 |
| AvalancheMask | 遮罩系统 | 待补充 |
| AvalancheRemoteControl | 远程控制集成 | 待补充 |
| 其他模块 | 场景树、标签、转场、MRQ 等 | 待补充 |

---

## 用途

Motion Design（原名 Avalanche，从 Experimental 迁移）是 UE5 的**虚拟制作动态设计工具套件**，为电视广播、现场活动、虚拟场景搭建提供完整的实时图形设计管线。

该插件解决的核心问题：

1. **3D 文本设计**：扩展引擎内置的 Text3D 组件，提供字体管理、材质着色（渐变、纹理、自定义材质）、半透明效果等专业功能
2. **材质桥接系统**：通过 Material Bridge 模式统一管理 Text3D 组件及其扩展的材质槽访问，支持状态保存/恢复
3. **动态图形管线**：整合克隆/效果器、属性动画、场景过渡、远程控制等，构建完整的 Motion Graphics 工作流
4. **广播输出**：集成媒体合成和 Movie Render Queue，支持实时输出和离线渲染

**AvalancheText 子模块**专注于 3D 文本的核心运行时功能：字体资产管理、文本组件扩展、材质桥接。

## 使用场景

- 你在制作电视节目的**实时字幕/标题图形** → 使用 Motion Design 的文本和材质系统
- 你需要为虚拟演唱会设计**动态 3D 标题动画** → 使用 AvalancheText 组件配合属性动画
- 你在搭建**虚拟演播室场景**，需要复杂的文字效果（渐变、纹理、半透明） → 使用材质桥接系统
- 你需要从系统字体库选择字体用于 3D 文本 → 使用 FAvaFont / UAvaFontObject 字体管理

---

# AvalancheText 子模块

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFont` | 获取当前字体（缺失时返回默认字体） | `FAvaFont` |
| `GetFontName` / `GetFontNameAsString` | 获取字体名称 | `FAvaFont` |
| `IsFavorite` / `SetFavorite` | 标记/查询收藏字体 | `FAvaFont` |
| `IsDefaultFont` | 检查是否为默认字体 | `FAvaFont` |
| `IsFallbackFont` | 检查是否因缺失资源而回退到默认字体 | `FAvaFont` |
| `IsMonospaced` / `IsBold` / `IsItalic` | 查询字体属性 | `FAvaFont` |
| `GetFontSource` | 获取字体来源（系统/项目/无效） | `FAvaFont` |
| `GetColorData` / `SetColorData` | 获取/设置文本颜色数据 | `AAvaTextActor` |

### 使用示例（蓝图描述）

**创建带自定义材质的 3D 文本：**
1. 在场景中放置 `AText3DActor`（替代已弃用的 `AAvaTextActor`）
2. 获取其 `UText3DComponent`，系统自动应用 `FText3DComponentMaterialBridge` 管理材质槽
3. 通过材质扩展（Material Extension）设置渐变、纹理等效果

**使用字体管理：**
1. 创建 `FAvaFont` 结构体 → 自动初始化为默认字体（Roboto）
2. 调用 `GetFont()` 获取 `UFont` 指针用于渲染
3. 通过 `UAvaFontObject` 管理系统字体和项目字体

---

## C++ 用法

### 头文件引入

```cpp
// 字体管理
#include "Font/AvaFont.h"
#include "Font/AvaFontObject.h"

// 文本组件
#include "AvaText3DComponent.h"
#include "AvaTextDefs.h"

// 材质桥接（如需自定义材质扩展）
#include "MaterialBridge/AvaText3DComponentMaterialBridge.h"
#include "MaterialBridge/AvaText3DExtensionMaterialBridge.h"
```

### 基本用法：字体管理

```cpp
// 来源: Public/Font/AvaFont.h

// 创建 FAvaFont（自动使用默认字体 Roboto）
FAvaFont Font;

// 获取 UFont 用于渲染（推荐的获取方式）
UFont* FontAsset = Font.GetFont();

// 检查字体状态
if (Font.IsFallbackFont())
{
    UE_LOG(LogTemp, Warning, TEXT("字体资产 '%s' 缺失，已回退到默认字体"), *Font.GetMissingFontName());
}

// 查询字体属性
bool bMonospaced = Font.IsMonospaced();
bool bBold = Font.IsBold();
bool bItalic = Font.IsItalic();

// 获取字体来源
EAvaFontSource Source = Font.GetFontSource(); // System, Project, 或 Invalid
```

### 基本用法：字体对象

```cpp
// 来源: Public/Font/AvaFontObject.h

// 初始化项目字体
UAvaFontObject* FontObject = NewObject<UAvaFontObject>();
FontObject->InitProjectFont(MyUFont, TEXT("MyCustomFont"));

// 初始化系统字体（从系统字体库）
FSystemFontsRetrieveParams Params;
Params.FontFamilyName = TEXT("Arial");
Params.AddFontFace(TEXT("Regular"), TEXT("/path/to/arial.ttf"));
FontObject->InitSystemFont(Params, SystemUFont);

// 查询字体度量
FAvaSystemFontMetrics Metrics = FontObject->GetMetrics();
if (Metrics.bIsBold)
{
    UE_LOG(LogTemp, Log, TEXT("这是粗体字体"));
}

// 获取字体面信息
TArray<const UFontFace*> FontFaces = FontObject->GetFontFaces();
```

### 基本用法：渐变设置

```cpp
// 来源: Public/AvaTextDefs.h

// 创建渐变设置
FAvaLinearGradientSettings Gradient;
Gradient.Direction = EAvaGradientDirection::Vertical;
Gradient.ColorA = FLinearColor(1.0f, 0.8f, 0.2f);  // 金黄色
Gradient.ColorB = FLinearColor(0.8f, 0.2f, 0.1f);  // 深红色
Gradient.Smoothness = 0.3f;
Gradient.Offset = 0.5f;
Gradient.Rotation = 0.0f;
```

### 进阶用法：材质桥接

```cpp
// 来源: Public/MaterialBridge/AvaText3DComponentMaterialBridge.h
// 材质桥接系统用于管理 Text3D 组件的材质槽访问

// 材质桥接层级:
// FMaterialBridge (基类)
//   └─ FText3DComponentMaterialBridge (Text3D 组件桥接)
//        └─ FText3DExtensionMaterialBridge (扩展桥接基类)
//             └─ FText3DDefaultExtensionMaterialBridge (默认扩展桥接)
//
// FText3DManagedComponentMaterialBridge: 管理型组件的桥接（委托给 Text3D 组件桥接）

// 获取材质桥接状态进行序列化
// FAvaText3DComponentMaterialStateData 包含:
//   - 继承自 FAvaMaterialContainerState 的基础状态
//   - MaterialExtensionStateData: 材质扩展的状态数据

// 读取材质槽
// EControlFlow Result = Bridge->OnAccessSlots(ReadContext, 
//     [](const FReadSlotContext& Ctx, const FReadSlot& Slot) -> EControlFlow
//     {
//         // 读取每个材质槽
//         return EControlFlow::Continue;
//     }, ReadOptions);
```

### 进阶用法：序列化兼容

```cpp
// 来源: Public/Font/AvaFont.h
// FAvaFont 使用 PostSerialize 处理旧版本兼容

// 序列化后的字体对象会自动处理:
// 1. 旧版 CurrentFont_DEPRECATED 字段迁移到 MotionDesignFontObject
// 2. 缺失的字体资产标记为 FallbackFont
// 3. 调用 EnsureUsingCurrentVersion() 手动迁移

// 手动迁移旧版字体引用
FAvaFont OldFont;
OldFont.EnsureUsingCurrentVersion();  // 将 CurrentFont 迁移到 MotionDesignFontObject

// 生成格式化字符串（用于 PropertyHandle 批量设置）
FString FormattedString;
if (FAvaFont::GenerateFontFormattedString(FontObject, FormattedString))
{
    // 用于 IPropertyHandle::SetPerObjectValues
}
```

---

## Demo 示例

### 3D 文本字体管理

```cpp
// AvaTextExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Font/AvaFont.h"
#include "Font/AvaFontObject.h"
#include "AvaTextExample.generated.h"

UCLASS()
class AAvaTextExample : public AActor
{
    GENERATED_BODY()

public:
    AAvaTextExample();

    /** 使用项目字体设置文本 */
    UFUNCTION(BlueprintCallable)
    void SetupTextWithProjectFont(UFont* InFont, const FString& InText);

    /** 使用系统字体设置文本 */
    UFUNCTION(BlueprintCallable)
    void SetupTextWithSystemFont(const FString& InFontFamilyName, const FString& InText);

    /** 获取当前字体名称 */
    UFUNCTION(BlueprintPure)
    FString GetCurrentFontName() const;

    /** 检查字体是否可用 */
    UFUNCTION(BlueprintPure)
    bool IsFontValid() const;

private:
    /** 当前使用的字体 */
    FAvaFont CurrentFont;

    /** 字体对象引用 */
    UPROPERTY()
    TObjectPtr<UAvaFontObject> FontObject;
};
```

```cpp
// AvaTextExample.cpp
#include "AvaTextExample.h"
#include "Font/AvaFont.h"
#include "Font/AvaFontObject.h"

AAvaTextExample::AAvaTextExample()
{
    PrimaryActorTick.bCanEverTick = false;
    FontObject = CreateDefaultSubobject<UAvaFontObject>(TEXT("FontObject"));
}

void AAvaTextExample::SetupTextWithProjectFont(UFont* InFont, const FString& InText)
{
    if (!InFont)
    {
        UE_LOG(LogTemp, Warning, TEXT("无效的字体资产"));
        return;
    }

    // 用项目字体初始化字体对象
    FontObject->InitProjectFont(InFont, InFont->GetName());
    
    // 用字体对象初始化 FAvaFont
    CurrentFont = FAvaFont(FontObject);

    // 验证字体是否有效
    if (CurrentFont.HasValidFont())
    {
        UE_LOG(LogTemp, Log, TEXT("文本 '%s' 使用字体 '%s'"), *InText, *CurrentFont.GetFontNameAsString());
    }
}

void AAvaTextExample::SetupTextWithSystemFont(const FString& InFontFamilyName, const FString& InText)
{
    // 构造系统字体查询参数
    FSystemFontsRetrieveParams Params;
    Params.FontFamilyName = InFontFamilyName;
    // 实际使用时需要通过系统字体枚举 API 添加 FontFace

    // 创建字体对象并初始化
    UAvaFontObject* SysFontObject = NewObject<UAvaFontObject>();
    // SysFontObject->InitSystemFont(Params, ResolvedUFont);  // 需要先解析系统字体

    // 标记为收藏
    CurrentFont.SetFavorite(true);

    UE_LOG(LogTemp, Log, TEXT("系统字体 '%s' 已标记为收藏"), *InFontFamilyName);
}

FString AAvaTextExample::GetCurrentFontName() const
{
    return CurrentFont.GetFontNameAsString();
}

bool AAvaTextExample::IsFontValid() const
{
    if (CurrentFont.IsFallbackFont())
    {
        UE_LOG(LogTemp, Warning, TEXT("字体回退: '%s' 缺失"), *CurrentFont.GetMissingFontName());
        return false;
    }
    return CurrentFont.HasValidFont();
}
```

---

## 模块依赖

`AvalancheText` 模块的 Build.cs 依赖信息未直接提供，但从头文件分析和插件描述可推断：

| 模块 | 用途 |
|---|---|
| `Text3D` | 基础 3D 文本组件（UAvaText3DComponent 继承自 UText3DComponent） |
| `AvalancheMaterial` | 材质桥接基类（FAvaMaterialBridgeFeature, FAvaMaterialContainerState） |

其余均为标准 Core/Engine 依赖。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将场景设置和大纲视图标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为 MRQ 添加节目单页面分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde… | 为节目控制工具栏添加页面加载选项 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes | 新增项目设置以禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with… | 重构视口客户端关联通知机制 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2025-05-09（从 Experimental 迁移至 VirtualProduction）
- **近期更新**：最近一周内有多次实质性提交，功能持续迭代
- **活跃度**：非常高，包含新功能（MRQ 分析、页面加载选项）和持续改进
- **已知限制**：`AAvaTextActor` 已弃用（5.6），应使用 `AText3DActor` 替代；旧版材质属性（ColoringStyle、GradientSettings 等）已迁移至 Material Extension 系统
- **推荐度**：强烈推荐用于虚拟制作和广播场景设计，特别是需要 3D 文本和动态图形的项目

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [AvalancheText 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheText)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)