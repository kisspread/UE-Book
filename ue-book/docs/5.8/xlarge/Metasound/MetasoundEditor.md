# MetaSound Editor

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints

| 属性 | 值 |
|---|---|
| 中文名 | 元音频编辑器 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、UI界面） |
| 模块 | `MetasoundEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-23 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound/Source/MetasoundEditor) | |

## 用途

MetasoundEditor 是 MetaSound 音频系统的核心编辑器工具模块。它提供了一个完整的、基于节点的可视化图形界面（EdGraph），让声音设计师能够在不编写代码的情况下，设计、构建和调试复杂的 MetaSound 音频资产。

该模块解决了以下核心问题：
1.  **可视化编辑**：将音频处理流程（DSP图）以直观的节点和连线形式呈现，便于设计和理解。
2.  **资产创建与管理**：提供创建、编辑、验证 MetaSound Source 和 MetaSound Patch 资产的全套工具链。
3.  **实时预览与调试**：支持在编辑器内直接播放 MetaSound，通过连接管理器（FGraphConnectionManager）和探针（Pin Inspector）实时监控节点的输入输出值，实现所见即所得的调试。
4.  **扩展性支持**：通过子系统（UMetaSoundEditorSubsystem）、模块接口（IMetasoundEditorModule）和图面板工厂（IMetaSoundGraphPanelPinFactory）等机制，允许其他插件或模块注册自定义节点、引脚类型、工具栏扩展和UI小部件，从而扩展编辑器的功能。

简而言之，MetasoundEditor 是 MetaSound 音频设计师的“IDE”，是连接音频设计理念与底层可执行音频图的关键桥梁。

## 使用场景

-   **创建交互式环境音效**：你需要设计一个根据玩家位置、天气和游戏时间动态变化的复杂环境声景 → 使用 MetaSound Editor 中的输入（Input）节点暴露游戏参数，连接调制节点（如 LFO、包络）来控制声音的音量、音高、滤波器等。
-   **制作程序化生成的音效**：你需要一系列每次播放都有细微差异的武器或魔法音效 → 在 MetaSound Editor 中使用随机节点（Random）、触发器（Trigger）和变量（Variable）来构建一个能够生成变化声音的算法图。
-   **设计复杂的音频混合与处理**：你需要对多个声音源进行高级路由、总线处理和效果链应用 → 使用 MetaSound Editor 的子图（Subgraph）、音频分析器（Analyzer）节点和各种 DSP 节点（滤波器、混响、动态处理等）来搭建专业的处理链。
-   **快速原型和迭代**：声音设计师需要快速尝试不同的音频想法，无需等待程序员实现 → 直接在 MetaSound Editor 中拖拽节点、连接引脚、调整参数并实时试听，快速迭代设计。

## 蓝图用法

MetasoundEditor 模块主要通过 `UMetaSoundEditorSubsystem` 和 `UMetaSoundEditorBuilderListener` 向蓝图暴露功能。以下按功能分组列出核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Or Begin Building MetaSound Asset` | 查找或开始编辑指定的 MetaSound 资产，返回一个 Builder 以便进行蓝图化构建。 | `UMetaSoundEditorSubsystem` |
| `Build To Asset` | 将蓝图中的 Builder 配置构建成一个可播放的 MetaSound 资产。可选地从模板 SoundWave 复制声音设置（如衰减、调制）。 | `UMetaSoundEditorSubsystem` |
| `Set Node Location` | 设置 Builder 中某个节点在编辑器图形界面中的位置。 | `UMetaSoundEditorSubsystem` |
| `Find Or Create Graph Input Metadata` | 查找或创建图输入的元数据（包含编辑器特有的范围信息，如浮点数的 Min/Max）。 | `UMetaSoundEditorSubsystem` |
| `Add Builder Delegate Listener` | 为 Builder 添加一个监听器对象（`UMetaSoundEditorBuilderListener`），用于响应 Builder 文档的各类变更事件。 | `UMetaSoundEditorSubsystem` |
| `On Graph Input Default Changed` | 委托。当图输入的默认值被更改时触发，提供详细的变更参数（`FGraphInputDefaultChangedArgs`）。 | `UMetaSoundEditorBuilderListener` |
| `On Page Added` | 委托。当新的页面（Page）被添加到 MetaSound 文档时触发。 | `UMetaSoundEditorBuilderListener` |

### 使用示例（蓝图描述）

**场景：通过蓝图创建并修改一个 MetaSound 的输入参数。**

1.  **获取 Builder**：使用 `Find Or Begin Building MetaSound Asset` 节点，输入一个已存在的 MetaSound 资产引用，获取到 `UMetaSoundBuilderBase` 对象。
2.  **监听变更**：调用 `Add Builder Delegate Listener` 节点，为上一步获得的 Builder 创建一个 `UMetaSoundEditorBuilderListener`。在该监听器的事件图表中，绑定 `On Graph Input Default Changed` 等事件。
3.  **修改默认值**：在某个时机（如按键按下），通过蓝图逻辑调用 Builder 上的 `Set Graph Input Default` 等函数，修改特定输入的默认值。此时，绑定的委托将会被触发。
4.  **构建资产**：在所有修改完成后，调用 `Build To Asset` 节点，将 Builder 当前的状态构建成一个新的 MetaSound 资产文件。

## C++ 用法

MetasoundEditor 模块的 C++ API 主要面向需要深度定制编辑器或进行自动化处理的开发者。

### 头文件引入

```cpp
#include "MetasoundEditorSubsystem.h"
#include "MetasoundEditorModule.h"
#include "MetasoundEditorBuilderListener.h"
```

### 基本用法

通过 `UMetaSoundEditorSubsystem` 获取编辑器子系统实例，并操作 MetaSound 的构建流程。

```cpp
// 来源: Public/MetasoundEditorSubsystem.h
#include "MetasoundEditorSubsystem.h"

// 获取编辑器子系统单例
UMetaSoundEditorSubsystem& EditorSubsystem = UMetaSoundEditorSubsystem::GetChecked();

// 查找或开始构建一个 MetaSound
TScriptInterface<IMetaSoundDocumentInterface> MyMetaSound = /* ... */;
EMetaSoundBuilderResult Result;
UMetaSoundBuilderBase* Builder = EditorSubsystem.FindOrBeginBuilding(MyMetaSound, Result);

if (Builder && Result == EMetaSoundBuilderResult::Succeeded)
{
    // 使用 Builder 进行一些操作...
    // 例如，设置某个节点在编辑器中的位置
    FMetaSoundNodeHandle SomeNodeHandle = /* ... */;
    FVector2D NewLocation(100.0f, 200.0f);
    EditorSubsystem.SetNodeLocation(Builder, SomeNodeHandle, NewLocation, Result);
}
```

### 进阶用法

注册自定义引脚类型和工具栏扩展。

```cpp
// 来源: Public/IMetaSoundGraphPanelPinFactory.h, Public/MetasoundEditorModule.h
#include "MetasoundEditorModule.h"
#include "IMetaSoundGraphPanelPinFactory.h"

// 在模块的 StartupModule 中注册自定义引脚类型
void FMyEditorModule::StartupModule()
{
    // 确保 MetaSoundEditor 模块已加载
    if (FModuleManager::Get().IsModuleLoaded(IMetasoundEditorModule::ModuleName))
    {
        IMetasoundEditorModule& MetaSoundEditorModule = FModuleManager::GetModuleChecked<IMetasoundEditorModule>(IMetasoundEditorModule::ModuleName);
        TSharedRef<IMetaSoundGraphPanelPinFactory> PinFactory = MetaSoundEditorModule.GetGraphPanelPinFactory();

        // 注册一种新的数据类型引脚
        FGraphPinParams Params;
        Params.PinColor = &FLinearColor::Yellow;
        PinFactory->RegisterPin(TEXT("MyCustomDataType"), Params);

        // 注册一个自定义的引脚部件创建委托（可选）
        PinFactory->RegisterDataTypePin(TEXT("MyCustomDataType"),
            IMetaSoundGraphPanelPinFactory::FOnCreateMetaSoundPinWidget::CreateLambda(
                [](UEdGraphPin* Pin) -> TSharedPtr<SGraphPin>
                {
                    // 返回一个自定义的引脚部件
                    return SNew(SMyCustomGraphPin, Pin);
                }
            )
        );

        // 注册工具栏扩展
        TSharedRef<FExtender> ToolbarExtender = MakeShared<FExtender>();
        ToolbarExtender->AddToolBarExtension(
            “Asset”,
            EExtensionHook::After,
            nullptr,
            FToolBarExtensionDelegate::CreateLambda([](FToolBarBuilder& Builder){ /* ... */ })
        );
        EditorSubsystem.RegisterToolbarExtender(ToolbarExtender);
    }
}

// 在模块的 ShutdownModule 中注销
void FMyEditorModule::ShutdownModule()
{
    if (FModuleManager::Get().IsModuleLoaded(IMetasoundEditorModule::ModuleName))
    {
        IMetasoundEditorModule& MetaSoundEditorModule = FModuleManager::GetModuleChecked<IMetasoundEditorModule>(IMetasoundEditorModule::ModuleName);
        TSharedRef<IMetaSoundGraphPanelPinFactory> PinFactory = MetaSoundEditorModule.GetGraphPanelPinFactory();
        PinFactory->UnregisterPin(TEXT("MyCustomDataType"));
        PinFactory->UnregisterDataTypePin(TEXT("MyCustomDataType"));
        // 注销工具栏扩展
        MetaSoundEditorModule.UnregisterToolbarExtender(ToolbarExtender);
    }
}
```

## Demo 示例

一个简单的示例，展示如何通过 C++ 子系统获取 Builder 并修改一个输入的显示名称。

**MyMetaSoundEditorUtility.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyMetaSoundEditorUtility.generated.h"

class UMetaSoundBuilderBase;
class IMetaSoundDocumentInterface;

UCLASS()
class UMyMetaSoundEditorUtility : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // 在 MetaSound 资产中查找一个名为 “MyInput” 的输入，并将其显示名称重命名为 “NewDisplayName”
    UFUNCTION(BlueprintCallable, Category = “MetaSound”)
    bool RenameMetaSoundInput(UObject* MetaSoundAsset, FName InputName, const FText& NewDisplayName);
};
```

**MyMetaSoundEditorUtility.cpp**
```cpp
#include "MyMetaSoundEditorUtility.h"
#include “MetasoundEditorSubsystem.h”

bool UMyMetaSoundEditorUtility::RenameMetaSoundInput(UObject* MetaSoundAsset, FName InputName, const FText& NewDisplayName)
{
    if (!MetaSoundAsset || !MetaSoundAsset->GetClass()->ImplementsInterface(UMetaSoundDocumentInterface::StaticClass()))
    {
        return false;
    }

    TScriptInterface<IMetaSoundDocumentInterface> MetaSoundDoc = MetaSoundAsset;
    if (!MetaSoundDoc)
    {
        return false;
    }

    // 获取编辑器子系统（仅在编辑器环境下有效）
    UMetaSoundEditorSubsystem* EditorSubsystem = GEditor ? GEditor->GetEditorSubsystem<UMetaSoundEditorSubsystem>() : nullptr;
    if (!EditorSubsystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("UMyMetaSoundEditorUtility::RenameMetaSoundInput: MetaSoundEditorSubsystem not available. This function only works in the editor."));
        return false;
    }

    // 获取或开始构建
    EMetaSoundBuilderResult Result;
    UMetaSoundBuilderBase* Builder = EditorSubsystem->FindOrBeginBuilding(MetaSoundDoc, Result);
    if (Result != EMetaSoundBuilderResult::Succeeded || !Builder)
    {
        return false;
    }

    // 通过 Builder 的接口获取输入控制器并重命名
    // 注意：此处为简化演示，实际API调用链可能更复杂，需要参考 Frontend 模块的 Builder API
    // MetaSound::Frontend::FConstInputHandle InputHandle = Builder->GetConstBuilder().GetInputHandle(InputName);
    // if (InputHandle.IsValid())
    // {
    //     Builder->GetBuilder().SetInputDisplayName(InputHandle, NewDisplayName);
    //     return true;
    // }

    // 由于完整的 Frontend Builder API 不在此模块演示范围内，此处仅展示流程。
    // 实际开发中，应使用 `FMetaSoundFrontendDocumentBuilder` 或对应的蓝图函数库。
    UE_LOG(LogTemp, Log, TEXT("Would rename input '%s' to '%s' on MetaSound: %s"), *InputName.ToString(), *NewDisplayName.ToString(), *MetaSoundAsset->GetName());
    return true; // 简化返回
}
```

## 模块依赖

MetasoundEditor 模块本身是 MetaSound 系统的一部分，但作为编辑器模块，它主要依赖 MetaSound 的核心模块。对于你的自定义模块，如果需要与 MetaSound 编辑器交互，通常需要依赖：

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | 提供 MetaSound 文档模型（Builder, Document, Node）的核心 C++ API，是编程式访问 MetaSound 结构的基础。 |
| `MetasoundEngine` | 提供运行时 MetaSound 资产（UMetaSoundSource, UMetaSoundPatch）和构建系统（FDocumentBuilderRegistry）。 |
| `MetasoundGraphCore` | 提供底层图（Graph）和节点（Node）的运行时表示，编辑器图与运行时图的同步依赖于此。 |

*注意：`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UMG`, `InputCore`, `UnrealEd`, `EditorStyle` 等为常见依赖，此处省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `17643970` | Fix ensure when deleting and re-adding a MetaSound Page graph | 修复了删除后重新添加 MetaSound 页面图时出现的断言错误。 |
| 2026-05-14 | `278def59` | Guard MetaSound preset creation against non-Referenceable parents | 保护 MetaSound 预设创建过程，防止父资产不可引用导致的错误。 |
| 2026-05-14 | `6121cd30` | Protect against mutation of target PageID in shipped builds | 保护已发布构建中目标页面ID不被意外修改。 |
| 2026-05-14 | `79768793` | Clean-up pass on prior fix for deadlock fix when entering PIE | 对先前修复进入PIE（编辑器内播放）时死锁问题的代码进行清理。 |
| 2026-05-14 | `de6200e1` | Speculative fix for freeze when entering PIE | 针对进入编辑器内播放时可能出现的界面冻结问题的推测性修复。 |

### 维护评价

MetasoundEditor 是 MetaSound 系统的活跃维护模块。
- **创建时间**：约5年前随 UE5 初版引入，相对较新。
- **近期活动**：最近一次更新就在撰写文档的当天（2026-05-14），且连续提交了5个修复提交，主要集中在**页面（Page）系统**的稳定性和**PIE（编辑器内播放）** 的可靠性上。这表明 Epic 工程团队正在集中解决复杂功能（页面、预设）的边界情况和已知问题。
- **维护状态**：**活跃维护中**。更新频率高，且针对用户使用流程中的关键痛点（如编辑器冻结、断言）进行修复。
- **已知限制**：从提交信息看，页面（Page）和预设（Preset）系统作为较新的实验性功能，可能仍存在一些稳定性问题。
- **推荐使用**：**强烈推荐**。MetaSound 是 Epic 重点发展的下一代音频系统，其编辑器工具是声音设计师的核心工作界面。尽管页面系统可能仍有些许边缘问题，但核心的图编辑、节点创建和实时预览功能已非常成熟和强大。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound/Source/MetasoundEditor)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-audio/sound-sources/meta-sounds/) (基于 FEditor 中的 GetDocumentationLink)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest) (测试模块在 MetasoundEngineTest 中)