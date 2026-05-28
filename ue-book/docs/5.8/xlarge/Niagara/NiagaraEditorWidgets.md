# Niagara Editor Widgets

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 编辑器控件 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（示例资产、材质、数据接口） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-28 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara) | |

> **说明**：本文档聚焦 **NiagaraEditorWidgets** 模块——Niagara 编辑器 UI 的 Slate 控件层。Niagara 整体插件规模达 1622 个源文件，属于 xlarge 级别，需按子模块拆分。完整文档应覆盖所有 8 个子模块。

---

## 用途

**NiagaraEditorWidgets** 是 Niagara 粒子编辑器的 **Slate 控件层**，它实现了编辑器中所有可视化的 UI 组件，包括：

- **Stack 面板**：Niagara 系统/发射器的模块堆栈编辑界面（`SNiagaraStack`），用户在此添加、排序、配置粒子行为模块。
- **Overview 面板**：系统总览图，以节点图形式展示发射器之间的关系和数据流（`SNiagaraOverviewGraph`、`SNiagaraOverviewStackNode`）。
- **属性面板细节定制**：为各类 Niagara 数据接口（曲线、网格、骨骼网格、渲染器等）提供自定义的 Details 面板 UI，替代默认属性编辑体验。
- **曲线编辑器集成**：内置的曲线编辑控件（`SNiagaraCurveOverview`、`SNiagaraCurveKeySelector`），用于编辑粒子系统中的各种曲线数据。
- **Scratch Pad**：临时脚本管理界面（`SNiagaraScratchPadScriptManager`），用于快速原型开发。

该模块不包含核心模拟逻辑或着色器编译，纯粹是编辑器 UI 层。运行时模拟由 `Niagara` 核心模块负责，编辑器逻辑由 `NiagaraEditor` 模块负责，而本模块提供所有 Slate Widget 的具体实现。

---

## 使用场景

- 你在编辑器中打开一个 Niagara 系统资产 → Stack 面板、Overview 图表均由本模块的控件渲染
- 你在 Details 面板中编辑一个 Curve 数据接口 → `FNiagaraDataInterfaceCurveDetails` 系列类提供嵌入式曲线编辑器
- 你使用拖拽将模块添加到发射器 Stack → `SNiagaraStackItemGroupAddMenu` 处理添加菜单和搜索过滤
- 你需要在 Stack 中查看性能统计信息 → `SNiagaraStackRowPerfWidget` 在每行显示 GPU/CPU 耗时

---

## 蓝图用法

本模块是纯 Slate 控件层，**不暴露蓝图 API**。所有 `UFUNCTION(BlueprintCallable)` 和 `UPROPERTY(BlueprintReadWrite)` 定义在 `Niagara`、`NiagaraBlueprintNodes` 等运行时/蓝图模块中。

如需在蓝图中与 Niagara 交互，请参考 **NiagaraBlueprintNodes** 模块文档。

---

## C++ 用法

### 模块加载

```cpp
#include "NiagaraEditorWidgetsModule.h"

// 获取模块实例
FNiagaraEditorWidgetsModule& EditorWidgetsModule = FNiagaraEditorWidgetsModule::Get();

// 通过模块提供的 Widget Provider 创建编辑器控件
TSharedRef<INiagaraEditorWidgetProvider> WidgetProvider = /* 从 DI 或模块获取 */;
TSharedRef<SWidget> StackView = WidgetProvider->CreateStackView(*StackViewModel);
TSharedRef<SWidget> SystemOverview = WidgetProvider->CreateSystemOverview(SystemViewModel, EditedAsset);
```

### 曲线编辑选项

```cpp
#include "NiagaraEditorWidgetsModule.h"

// 为特定对象创建/获取曲线编辑器选项（用于 Stack 中的曲线编辑控件）
FNiagaraEditorWidgetsModule& Module = FNiagaraEditorWidgetsModule::Get();
TSharedRef<FNiagaraStackCurveEditorOptions> Options = 
    Module.GetOrCreateStackCurveEditorOptionsForObject(MyObject, 200.0f);

// 配置视图范围
Options->SetInputViewRange(0.0f, 10.0f);
Options->SetOutputViewRange(-1.0f, 1.0f);
Options->SetIsGradientVisible(true);
```

### 属性面板细节定制注册

```cpp
// 数据接口细节定制通常在 NiagaraEditor 模块中注册，
// 但控件实现位于本模块。
// 示例：注册曲线数据接口的细节定制
PropertyModule.RegisterCustomClassLayout(
    UNiagaraDataInterfaceCurve::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FNiagaraDataInterfaceCurveDetails::MakeInstance));
```

---

## 核心控件一览

### Stack 相关控件

| 控件 | 说明 | 所在文件 |
|---|---|---|
| `SNiagaraStack` | 主 Stack 面板，树形视图展示所有模块/项 | `Private/SNiagaraStack.h` |
| `SNiagaraStackTableRow` | Stack 中每一行的表格行控件，支持拖拽、展开/折叠、搜索高亮 | `Private/Stack/SNiagaraStackTableRow.h` |
| `SNiagaraStackModuleItem` | 单个模块项的控件，支持版本选择、脚本重分配 | `Private/Stack/SNiagaraStackModuleItem.h` |
| `SNiagaraStackItem` | Stack 条目的基类控件，包含启用/禁用复选框、删除按钮 | `Private/Stack/SNiagaraStackItem.h` |
| `SNiagaraStackFunctionInputValue` | 函数输入值编辑器，支持本地值/链接/动态输入多种模式 | `Private/Stack/SNiagaraStackFunctionInputValue.h` |
| `SNiagaraStackFunctionInputName` | 函数输入名称显示，支持重命名、命名空间修改 | `Private/Stack/SNiagaraStackFunctionInputName.h` |
| `SNiagaraStackInlineDynamicInput` | 内联动态输入控件，将嵌套的函数调用渲染为紧凑的表达式视图 | `Private/Stack/SNiagaraStackInlineDynamicInput.h` |
| `SNiagaraStackItemGroupAddMenu` | 添加模块/项的搜索菜单，支持分类过滤和库/项目筛选 | `Private/Stack/SNiagaraStackItemGroupAddMenu.h` |
| `SNiagaraStackRowPerfWidget` | 性能统计条，显示每个模块的 GPU/CPU 执行时间 | `Private/Stack/SNiagaraStackRowPerfWidget.h` |
| `SNiagaraStackNote` | Stack 中的注释/备注控件 | `Private/SNiagaraStackNote.h` |
| `SNiagaraStackIssueIcon` | 问题/警告图标，显示编译错误或兼容性问题 | `Private/Stack/SNiagaraStackIssueIcon.h` |
| `SNiagaraStackScriptHierarchyRoot` | 脚本层级分区选择器 | `Private/Stack/SNiagaraStackScriptHierarchyRoot.h` |

### Overview 相关控件

| 控件 | 说明 | 所在文件 |
|---|---|---|
| `SNiagaraOverviewGraph` | 系统总览节点图，展示发射器关系 | `Private/SNiagaraOverviewGraph.h` |
| `SNiagaraOverviewStackNode` | 总览图中的发射器节点，含缩略图、启用开关、隔离按钮 | `Private/SNiagaraOverviewStackNode.h` |
| `SNiagaraOverviewStack` | 总览堆栈面板，列表形式展示发射器 | `Private/SNiagaraOverviewStack.h` |
| `SNiagaraOverviewGraphTitleBar` | 总览图标题栏，显示编译模式和系统状态 | `Private/SNiagaraOverviewGraphTitleBar.h` |
| `SNiagaraOverviewInlineParameterBox` | 总览节点内嵌的参数展示区 | `Private/SNiagaraOverviewInlineParameterBox.h` |

### 数据接口细节定制

| 类 | 说明 | 所在文件 |
|---|---|---|
| `FNiagaraDataInterfaceDetailsBase` | 数据接口细节定制基类，处理错误显示和自定义节点构建 | `Private/DetailCustomizations/NiagaraDataInterfaceDetails.h` |
| `FNiagaraDataInterfaceCurveDetailsBase` | 曲线数据接口细节定制基类，支持资产导入、渐变显示、曲线编辑器集成 | `Private/DetailCustomizations/NiagaraDataInterfaceCurveDetails.h` |
| `FNiagaraDataInterfaceCurveDetails` | Float 曲线细节定制 | 同上 |
| `FNiagaraDataInterfaceVector2DCurveDetails` | 2D 向量曲线细节定制 | 同上 |
| `FNiagaraDataInterfaceVectorCurveDetails` | 3D 向量曲线细节定制 | 同上 |
| `FNiagaraDataInterfaceVector4CurveDetails` | 4D 向量曲线细节定制 | 同上 |
| `FNiagaraDataInterfaceColorCurveDetails` | 颜色曲线细节定制 | 同上 |
| `FNiagaraDataInterfaceSkeletalMeshDetails` | 骨骼网格数据接口细节定制，含骨骼/Socket/区域选择 | `Private/DetailCustomizations/NiagaraDataInterfaceSkeletalMeshDetails.h` |
| `FNiagaraDataInterfaceStaticMeshDetails` | 静态网格数据接口细节定制，含 Socket 选择 | `Private/DetailCustomizations/NiagaraDataInterfaceStaticMeshDetails.h` |
| `FNiagaraDataInterfaceMeshRendererInfoDetails` | 网格渲染器信息接口细节定制 | `Private/DetailCustomizations/NiagaraDataInterfaceMeshRendererInfoDetails.h` |
| `FNiagaraDataInterfaceSpriteRendererInfoDetails` | 精灵渲染器信息接口细节定制 | `Private/DetailCustomizations/NiagaraDataInterfaceSpriteRendererInfoDetails.h` |
| `FNiagaraDataInterfaceGrid2DCollectionDetails` | 2D 网格集合细节定制 | `Private/DetailCustomizations/NiagaraDataInterfaceGrid2DCollectionDetails.h` |
| `FNiagaraDataInterfaceGrid3DCollectionDetails` | 3D 网格集合细节定制 | `Private/DetailCustomizations/NiagaraDataInterfaceGrid3DCollectionDetails.h` |
| `FNiagaraDataInterfaceSocketReaderDetails` | Socket 读取器细节定制 | `Private/DetailCustomizations/NiagaraDataInterfaceSocketReaderDetails.h` |
| `FNiagaraDataChannelIslandsDetails` | 数据通道岛屿细节定制 | `Private/DetailCustomizations/NiagaraDataChannelDetails.h` |
| `FNiagaraDataInterfaceDataChannelReadDetails` | 数据通道读取接口细节定制 | 同上 |

### 曲线与其他控件

| 控件 | 说明 | 所在文件 |
|---|---|---|
| `SNiagaraCurveOverview` | 系统级曲线编辑器概览面板 | `Private/SNiagaraCurveOverview.h` |
| `SNiagaraCurveKeySelector` | 曲线关键帧选择/导航控件 | `Private/SNiagaraCurveKeySelector.h` |
| `SNiagaraScratchPadScriptManager` | 临时脚本管理器 | `Private/SNiagaraScratchPadScriptManager.h` |
| `SNiagaraScalabilityPreviewSettings` | 可伸缩性预览设置控件 | `Private/SNiagaraScalabilityPreviewSettings.h` |
| `SNiagaraEmitterRendererThumbnails` | 发射器渲染器缩略图 | `Private/SNiagaraEmitterRendererThumbnails.h` |
| `SNiagaraParameterDropTarget` | 参数拖放目标控件 | `Private/SNiagaraParameterDropTarget.h` |
| `SNiagaraNamePropertySelector` | 名称属性选择下拉框 | `Private/DetailCustomizations/SNiagaraNamePropertySelector.h` |

---

## 架构概览

```
NiagaraEditorWidgetsModule (入口)
├── FNiagaraEditorWidgetProvider (实现 INiagaraEditorWidgetProvider)
│   ├── CreateStackView()         → SNiagaraStack
│   ├── CreateSystemOverview()    → SNiagaraOverviewGraph
│   ├── CreateStackIssueIcon()    → SNiagaraStackIssueIcon
│   ├── CreateScriptScratchPadManager() → SNiagaraScratchPadScriptManager
│   ├── CreateCurveOverview()     → SNiagaraCurveOverview
│   ├── CreateCurveKeySelector()  → SNiagaraCurveKeySelector
│   └── CreateCurveThumbnail()    → 缩略图控件
│
├── Stack 面板
│   ├── SNiagaraStack (树形主视图)
│   ├── SNiagaraStackTableRow (行容器)
│   │   ├── SNiagaraStackItem (基类)
│   │   ├── SNiagaraStackModuleItem
│   │   └── SNiagaraStackFunctionInputValue
│   └── SNiagaraStackItemGroupAddMenu (添加菜单)
│
├── Overview 面板
│   ├── SNiagaraOverviewGraph (节点图)
│   ├── SNiagaraOverviewStackNode (图节点)
│   └── SNiagaraOverviewStack (列表视图)
│
└── Details 定制 (注册在 PropertyEditor)
    ├── 曲线系列 (Curve/Vector2D/Vector/Vector4/Color)
    ├── 网格系列 (StaticMesh/SkeletalMesh)
    ├── 渲染器系列 (MeshRenderer/SpriteRenderer)
    └── 其他 (Grid2D/Grid3D/SocketReader/DataChannel)
```

---

## Demo 示例

```cpp
// NiagaraCustomStackWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "ViewModels/Stack/NiagaraStackViewModel.h"

// 自定义 Stack 容器，演示如何使用 NiagaraEditorWidgets 提供的控件
class SNiagaraCustomStackContainer : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SNiagaraCustomStackContainer) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, UNiagaraStackViewModel* InViewModel)
    {
        ChildSlot
        [
            SNew(SVerticalBox)

            // 标题
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(4.0f)
            [
                SNew(STextBlock)
                .Text(FText::FromString(TEXT("Custom Niagara Stack")))
                .Font(FCoreStyle::GetDefaultFontStyle("Bold", 14))
            ]

            // Stack 视图（由 NiagaraEditorWidgets 模块提供）
            + SVerticalBox::Slot()
            .FillHeight(1.0f)
            [
                // 方式一：通过模块直接创建 Stack 控件
                // FNiagaraEditorWidgetsModule::Get().GetWidgetProvider().CreateStackView(*InViewModel)

                // 方式二：直接实例化 Stack 控件
                SAssignNew(StackWidget, SNiagaraStack)
            ]
        ];
    }

private:
    TSharedPtr<SNiagaraStack> StackWidget;
};
```

```cpp
// NiagaraCustomDetailsPanel.h
#pragma once

#include "CoreMinimal.h"
#include "DetailCustomizations/NiagaraDataInterfaceCurveDetails.h"

// 自定义曲线数据接口细节面板（继承自内置细节定制基类）
class FMyCustomCurveDetails : public FNiagaraDataInterfaceCurveDetailsBase
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance()
    {
        return MakeShareable(new FMyCustomCurveDetails());
    }

protected:
    // 获取要显示的曲线属性
    virtual void GetCurveProperties(
        IDetailLayoutBuilder& DetailBuilder,
        TArray<TSharedRef<IPropertyHandle>>& OutCurveProperties) const override
    {
        // 引用 NiagaraDataInterfaceCurve 中的 FloatCurve 属性
        TSharedRef<IPropertyHandle> CurveProp = 
            DetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UNiagaraDataInterfaceCurveBase, FloatCurves));
        OutCurveProperties.Add(CurveProp);
    }

    // 支持的资产类型（用于导入）
    virtual FTopLevelAssetPath GetSupportedAssetClassName() const override
    {
        return FTopLevelAssetPath(UCurveFloat::StaticClass());
    }

    // 从资产提取浮点曲线数据
    virtual void GetFloatCurvesFromAsset(
        UObject* SelectedAsset,
        TArray<FRichCurve>& FloatCurves) const override
    {
        if (UCurveFloat* FloatCurve = Cast<UCurveFloat>(SelectedAsset))
        {
            FloatCurves.Add(FloatCurve->FloatCurve);
        }
    }
};
```

---

## 模块依赖

本模块主要依赖 Niagara 生态内部模块及 Slate 标准模块。

| 模块 | 用途 |
|---|---|
| `NiagaraCore` | Niagara 核心类型定义（变量、类型定义等） |
| `NiagaraEditor` | 编辑器视图模型（Stack ViewModel、System ViewModel 等） |
| `NiagaraShader` | 着色器相关类型（用于材质预览等） |
| `CurveEditor` | 曲线编辑器框架（Engine 内置） |
| `PropertyEditor` | 属性面板框架（用于 Details 定制注册） |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `da97a493` | Data Hierarchy: guard SyncViewModelsToData against re-entry from OnHierarchyChanged listeners | 数据层级：防止 SyncViewModelsToData 重入导致递归问题 |
| 2026-05-22 | `85c6d110` | - Avoid creating an empty RHI buffer for SKM sampling data | 避免为骨骼网格采样数据创建空 RHI 缓冲区 |
| 2026-05-20 | `119ee9ac` | [HWRT] Fix FNiagaraRendererMeshes::GetDynamicRayTracingInstances(...) corrupting GPUScene when rende | 修复硬件光线追踪中网格渲染器损坏 GPUScene 的问题 |
| 2026-05-19 | `5e68c5a9` | [HWRT] Fix crash due to FNiagaraRendererRibbons requesting multiple updates on the same RayTracingGe | 修复带状渲染器重复请求 RayTracing 几何体更新导致的崩溃 |
| 2026-05-14 | `4bb8e4f1` | Fix UNiagaraBakerSettings crash when AI toolset or Python writes a null entry into the Outputs array | 修复烘焙设置在 AI 工具或 Python 写入空条目时的崩溃 |

### 维护评价

**活跃维护** 🟢

- Niagara 是 Epic 的旗舰粒子系统，**持续受到高强度开发维护**（Paragon、Fortnite、UE5 默认粒子系统均依赖它）
- 2026 年 5 月仍有密集提交，涵盖硬件光线追踪支持、性能优化、Bug 修复
- 创建于 2017 年，经历了从 Experimental 到默认启用的完整生命周期
- 8 个子模块结构清晰，代码量极大（1622 源文件），文档和测试覆盖相对完善
- **强烈推荐使用**：这是 UE5 唯一推荐的粒子系统（Cascade 已废弃）
- 已知限制：模块数量多导致首次编译时间较长

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara)
- [源码（EditorWidgets）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara/Source/NiagaraEditorWidgets)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/creating-visual-effects-in-niagara-for-unreal-engine)