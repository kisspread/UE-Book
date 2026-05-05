# Text 3D

> Tool to create 3D Text with advanced options

| 属性 | 值 |
|---|---|
| 分类 | Text |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、字体资产） |
| 模块 | `Text3D` (Runtime), `Text3DEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Text3D) | |

## 用途

Text3D 插件为虚幻引擎提供了在运行时和编辑器中创建、渲染和动画化高质量3D文本的能力。它不仅仅是一个简单的文本显示工具，而是一个功能完备的3D文本生成系统，解决了在虚拟制作、UI设计、动态标题和品牌展示等场景中需要复杂、可定制化3D文字的需求。其核心是通过 `UText3DComponent` 将文本字符串转换为可渲染的3D几何体，并支持丰富的材质、动画和排版控制。

## 使用场景

- **虚拟制作 (Virtual Production)**：在LED墙或虚拟场景中创建动态的3D标题、Logo或信息牌。
- **游戏内UI/HUD**：制作具有深度感、可旋转、可动画化的游戏内界面元素。
- **建筑可视化 (ArchViz)**：为建筑模型添加可定制的3D门牌号、标识或说明文字。
- **动态品牌展示**：在宣传片或交互式体验中，创建可随音乐或用户交互而变化的3D文字动画。
- **数据可视化**：将数据（如数字、标签）以3D形式呈现在场景中。

## 蓝图用法

核心功能通过 `UText3DComponent` 暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Text` | 设置要显示的文本字符串 | `UText3DComponent` |
| `Set Font` | 设置用于生成字形的字体资产 | `UText3DComponent` |
| `Set Material` | 设置应用于3D文本网格的材质 | `UText3DComponent` |
| `Set Extrude` | 设置文本的挤出深度（厚度） | `UText3DComponent` |
| `Set Bevel` | 设置文本边缘的倒角参数 | `UText3DComponent` |
| `Set Scale` | 设置文本的整体缩放 | `UText3DComponent` |
| `Set Horizontal Alignment` | 设置文本的水平对齐方式（左、中、右） | `UText3DComponent` |
| `Set Vertical Alignment` | 设置文本的垂直对齐方式（顶、中、底） | `UText3DComponent` |
| `Set Word Spacing` | 设置单词之间的间距 | `UText3DComponent` |
| `Set Line Spacing` | 设置行间距 | `UText3DComponent` |
| `Set Character Spacing` | 设置字符之间的间距 | `UText3DComponent` |
| `Set Animation State` | 控制文本的动画状态（如打字机效果） | `UText3DComponent` |
| `Get Text Mesh` | 获取生成的文本静态网格体资产引用 | `UText3DComponent` |

### 使用示例（蓝图描述）

1.  **创建基础3D文本**：
    *   在 Actor 蓝图中，添加一个 `Text3DComponent`。
    *   在细节面板或通过 `Set Text` 节点设置 `Text` 属性为 “Hello World”。
    *   通过 `Set Font` 节点指定一个字体（如引擎自带的 Roboto）。
    *   调整 `Extrude`、`Bevel`、`Scale` 等属性以获得所需的3D外观。

2.  **创建动画文本**：
    *   使用 `Set Animation State` 节点，将状态设置为 `Typing`。
    *   通过 `Set Animation Speed` 控制打字速度。
    *   可以使用时间轴或事件驱动来触发动画的开始、暂停和重置。

3.  **动态改变文本**：
    *   在事件图表中，使用 `Set Text` 节点连接到一个变量或函数输出，实现文本内容的动态更新。

## C++ 用法

### 头文件引入

```cpp
#include "Components/Text3DComponent.h"
#include "Text3DTypes.h"
```

### 基本用法

创建并配置一个 `Text3DComponent`。

```cpp
// 在 Actor 的构造函数或 BeginPlay 中
UText3DComponent* Text3DComp = CreateDefaultSubobject<UText3DComponent>(TEXT("My3DText"));
Text3DComp->SetText(FText::FromString(TEXT("UE5 Text3D")));
Text3DComp->SetExtrude(10.0f); // 设置挤出深度
Text3DComp->SetBevel(2.0f);    // 设置倒角
Text3DComp->SetScale(FVector(1.0f, 1.0f, 1.0f));

// 设置材质（需要先加载或引用一个材质资产）
UMaterialInterface* TextMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_Text3D"));
if (TextMaterial)
{
    Text3DComp->SetMaterial(0, TextMaterial);
}
```

### 进阶用法

控制文本动画和响应文本生成完成事件。

```cpp
// 开始打字机动画
Text3DComp->SetAnimationState(EText3DAnimationState::Typing);
Text3DComp->SetAnimationSpeed(0.5f); // 每个字符0.5秒

// 绑定文本网格生成完成的委托
Text3DComp->OnTextMeshGenerated.AddUObject(this, &AMyActor::OnTextMeshReady);

void AMyActor::OnTextMeshReady(UText3DComponent* Component, UStaticMesh* GeneratedMesh)
{
    // 文本网格已生成，可以进行后续操作，例如应用物理或特效
    UE_LOG(LogTemp, Log, TEXT("Text mesh generated: %s"), *GeneratedMesh->GetName());
}
```

## Demo 示例

一个最小的可编译示例，展示如何在 C++ Actor 中创建和配置 Text3DComponent。

**MyText3DActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
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
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Text3D")
    UText3DComponent* Text3DComponent;
};
```

**MyText3DActor.cpp**
```cpp
#include "MyText3DActor.h"
#include "Components/Text3DComponent.h"

AMyText3DActor::AMyText3DActor()
{
    PrimaryActorTick.bCanEverTick = false;

    Text3DComponent = CreateDefaultSubobject<UText3DComponent>(TEXT("3DText"));
    RootComponent = Text3DComponent;

    // 设置默认文本和属性
    Text3DComponent->SetText(FText::FromString(TEXT("Hello 3D!")));
    Text3DComponent->SetExtrude(5.0f);
    Text3DComponent->SetBevel(1.0f);
}

void AMyText3DActor::BeginPlay()
{
    Super::BeginPlay();

    // 可以在运行时修改属性
    Text3DComponent->SetAnimationState(EText3DAnimationState::Typing);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FreeType2` | 用于解析字体文件（如 .ttf, .otf）并生成字形轮廓数据。 |
| `HarfBuzz` | 用于复杂的文本排版（如阿拉伯语、印地语等复杂文字系统的塑形和连字）。 |
| `MeshMergeUtilities` | 用于将生成的多个文本字形网格体合并为一个优化的静态网格体。 |
| `DirectX` | (Text3DEditor) 编辑器模块可能用于特定的渲染或预览功能。 |

## 维护状态

### 近期更新

```
- e645d738b062 MotionDesign : Text3D - Moving Text3D plugin outside of Experimental and into VirtualProduction
```
*解读：这是最近一次提交，将插件从实验性（Experimental）目录正式迁移到了虚拟制作（VirtualProduction）目录，标志着该插件已达到稳定和生产就绪状态。*

### 维护评价

- **创建时间**：插件创建于2019年，已有约6年历史。
- **最近更新**：最近一次实质性更新是将其从实验性状态毕业，迁移到正式目录。这表明 Epic 认为其功能已稳定。
- **活跃度**：基于提供的有限 git 历史，近期没有频繁的功能性提交，但作为 Epic 官方维护的 Virtual Production 工具链的一部分，其稳定性和兼容性会随着引擎版本更新而得到保障。
- **已知限制**：作为 xlarge 规模的插件，其内部实现复杂，可能对性能有较高要求，尤其是在处理大量动态文本时。依赖 FreeType2 和 HarfBuzz 也意味着需要处理字体授权问题。
- **推荐使用**：**推荐**。对于需要在虚幻引擎中创建高质量、可定制化3D文本的项目，尤其是虚拟制作领域，这是一个官方提供的强大且成熟的解决方案。虽然它不是默认启用的，但其功能完备，文档和示例（尽管需要从源码挖掘）相对齐全。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Text3D)
- [官方文档]() (暂无)
- [测试用例]() (需在引擎源码中搜索 `Text3D` 相关的自动化测试)