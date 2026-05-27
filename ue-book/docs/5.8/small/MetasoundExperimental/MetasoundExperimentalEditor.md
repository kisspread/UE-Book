# Metasound Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | MetaSound实验性功能 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

此插件是 Epic Games 为 MetaSound 音频系统开发的“实验场”。它包含**正在开发中、尚未准备好集成到主 MetaSound 插件（`Metasound`）的前沿功能、节点和资产类型**。其目的是让开发者（尤其是音频程序员和技术美术）能够提前试用、测试和反馈这些新特性，例如全新的滤波器、声音生成节点或工作流程改进。它本质上是 MetaSound 功能的“Beta 版”集合。

## 使用场景

-   **你是音频开发者或技术美术**，希望尝试 MetaSound 最新的节点和功能，例如“通道无关波形”(CAT Wave)、“梯形滤波器”或“乘法节点”。
-   **你正在为项目探索新的音频处理可能性**，需要访问那些尚未正式发布、但可能在未来成为标准的 MetaSound 实验性功能。
-   **你希望参与 MetaSound 的早期功能测试和反馈**，为 UE5 音频工具链的进化做出贡献。

## 蓝图用法

根据提供的源码分析，此插件的当前模块主要提供了**编辑器端的资产定义和节点配置自定义功能**，而非直接的运行时蓝图节点。

### 编辑器资产与自定义

| 功能 | 说明 | 所在类 |
|---|---|---|
| `CatSoundWaveContainer` 资产定义 | 在内容浏览器中定义并显示一种名为 “CatSoundWaveContainer” 的实验性资产类型。 | `UAssetDefinition_CatSoundWaveContainer` |
| `CatSoundWaveContainer` 资产创建 | 提供通过工厂模式创建 “CatSoundWaveContainer” 资产的功能。 | `UCatSoundWaveContainerFactory` |
| `CatSoundWaveContainer` 右键菜单 | 向编辑器内容浏览器的右键菜单中添加针对 “CatSoundWaveContainer” 的操作。 | `FCatSoundWaveContainerExtension` |
| 映射函数节点配置 | 为特定的 MetaSound 节点（如映射函数节点）在细节面板中提供高度自定义的 UI，例如集成曲线编辑器。 | `FMappingFunctionNodeConfigurationCustomization` |
| 示例节点配置 | 为示例节点提供简单的细节面板自定义，如显示特定的浮点属性。 | `FExampleWidgetNodeConfigurationCustomization` |
| 颗粒节点配置 | 为颗粒节点提供细节面板自定义，允许配置包络类型。 | `FGranularNodeConfigurationCustomization` |

### 使用示例（蓝图描述）

由于这些类主要工作在编辑器中，其用法更多体现在操作流程上：
1.  **启用插件**：在 `Edit -> Plugins` 中搜索 “Metasound Experimental” 并启用，重启编辑器。
2.  **创建新资产**：在内容浏览器右键，查找并创建 “CatSoundWaveContainer” 类型的资产。
3.  **使用实验性节点**：在 MetaSound 编辑器中，查找并使用那些标记为实验性的新节点（如梯形滤波器、乘法节点等）。选中节点后，在其“细节”面板中，你可能会看到此插件提供的、经过高度自定义的配置界面（例如曲线编辑器）。

## C++ 用法

### 头文件引入

对于编辑器模块的功能，主要需要在编辑器模块中引入相关头文件。
```cpp
#include "MetasoundMappingFunctionDetailsCustomization.h"
// 或其他具体的细节定制头文件
```

### 基本用法

此插件当前提供的 C++ API 主要面向编辑器扩展，用于自定义特定 MetaSound 节点的细节面板。
（注：由于提供的头文件均为编辑器相关，以下示例基于编辑器模块代码逻辑）

```cpp
// 假设你需要为自定义的 MetaSound 节点提供一个带曲线编辑器的细节面板
// 你需要继承 Metasound::Editor::FMetaSoundNodeConfigurationCustomization
// 并实现 FCurveOwnerInterface（如果需要曲线编辑功能）。
// 参考代码逻辑（简化自 FMappingFunctionNodeConfigurationCustomization）：

class FMyNodeConfigurationCustomization : public Metasound::Editor::FMetaSoundNodeConfigurationCustomization, public FCurveOwnerInterface
{
public:
    FMyNodeConfigurationCustomization(TSharedPtr<IPropertyHandle> InStructProperty, TWeakObjectPtr<UMetasoundEditorGraphNode> InNode)
        : FMetaSoundNodeConfigurationCustomization(InStructProperty, InNode)
    {
        // 初始化，绑定属性句柄
        CurvePropertyHandle = InStructProperty->GetChildHandle(GET_MEMBER_NAME_CHECKED(FMyNodeConfig, Curve));
        RuntimeCurve = ...; // 获取实际曲线数据
    }

    // 重写以添加自定义子行（例如，插入曲线编辑器）
    virtual void OnChildRowAdded(IDetailPropertyRow& ChildRow) override
    {
        // 创建并添加 SCurveEditor 控件
        CurveEditorWidget = SNew(SCurveEditor)
            .ViewMinInput(0.0f)
            .ViewMaxInput(1.0f)
            // ... 其他配置
            .OnCurveCommitted(FOnCurveCommitted::CreateSP(this, &FMyNodeConfigurationCustomization::OnCurveChanged));

        ChildRow.CustomWidget()
        .NameContent()
        [
            SNew(STextBlock)
            .Text(NSLOCTEXT("MyNode", "Curve", "Curve"))
        ]
        .ValueContent()
        [
            CurveEditorWidget.ToSharedRef()
        ];
    }

    // 实现 FCurveOwnerInterface 必需的虚函数，以处理曲线数据变更
    virtual void OnCurveChanged(const TArray<FRichCurveEditInfo>& ChangedCurveEditInfos) override
    {
        // 将编辑器中的曲线修改同步回节点数据结构
        // ...
        // 通知节点属性已更改
        UpdateMappingFunctionData();
    }

    // ... 其他必要的虚函数实现 ...
};
```

## Demo 示例

由于此插件的示例更多体现在编辑器交互和实验性节点的使用上，一个完整的、可编译的 C++ 最小示例需要依赖具体的实验性节点类定义。一个典型的使用场景描述如下：

**场景：** 你想在自己的 MetaSound 中尝试使用“梯形滤波器”节点。
1.  确保已启用 `MetasoundExperimental` 插件。
2.  打开 MetaSound 编辑器。
3.  在节点列表（通常通过右键菜单或搜索）中查找名为 “Ladder Filter” 或类似名称的实验性节点。
4.  将该节点拖拽到图表中，并连接其输入输出（如音频输入、滤波器参数、音频输出）。
5.  选中该节点，在“细节”面板中配置其属性。如果此节点的细节面板经过了此插件中类似 `FGranularNodeConfigurationCustomization` 的类自定义，你可能会看到特殊的配置界面。
6.  播放音频，实时调整参数，感受新滤波器的效果。

## 模块依赖

要在你的模块中使用此插件暴露的功能，你需要：
1.  **启用插件**：在项目的 `.uproject` 文件中添加插件依赖，或在编辑器中手动启用。
2.  **添加模块依赖**：在你的模块（`.Build.cs` 文件）中，根据你需要使用的功能，添加对以下模块的依赖：
    -   对于编辑器自定义功能，可能需要依赖 `MetasoundExperimentalEditor`。
    -   对于运行时实验性节点或功能，可能需要依赖 `MetasoundExperimentalRuntime` 或 `MetasoundExperimentalEngineRuntime`。
    -   核心依赖是 `Metasound` 插件本身。

| 模块 | 用途 |
|---|---|
| `Metasound` | 提供基础的 MetaSound 运行时和编辑器功能，是此插件的前提依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 添加了实验性的 MetaSound 通道无关类型（CAT）波形 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃修复的合并冲突。 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | [CAT] 乘法节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | [CAT] 梯形滤波器节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从待处理变更列表‘52759261’中取出（提交） |

### 维护评价

**活跃开发中，但为实验性质。**
-   **创建时间**：插件于 2025 年 4 月创建，非常新。
-   **更新频率**：从提交记录看，在 2026 年 4 月和 5 月仍有密集的功能性提交，专注于添加新的 CAT 节点（乘法、梯形滤波器、波形容器），表明该插件**正在被积极开发和迭代**。
-   **维护状态**：作为 `IsExperimentalVersion: true` 的插件，其功能和 API **不稳定，可能频繁更改或被移除**。它主要用于内部和先锋用户测试。
-   **推荐使用**：**仅推荐用于原型设计、技术预研和个人实验**。不建议在生产环境中依赖此插件中的任何功能，因为它们可能在未来版本中发生 breaking changes 或直接被删除。如果你是音频爱好者或早期采用者，可以大胆尝试以体验最新技术。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
-   [官方文档] 无
-   [测试用例] 无（在提供的信息中未发现独立的测试文件路径）