# Color Grading

> Adds a panel with detailed color grading controls

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ColorGradingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-06-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ColorGrading) | |

## 用途

Color Grading 插件为 UE5 编辑器提供了一个专业的色彩校正面板，通过可视化色轮（Color Wheel）替代传统的属性滑块，让用户可以直观地调整后处理体积（PostProcessVolume）和摄像机（CameraActor）的色彩分级参数。

该插件的核心价值在于将 `FPostProcessSettings` 中散落在属性面板各处的 Color Grading 相关属性，以 **5 个色轮**（Saturation、Contrast、Gamma、Gain、Offset）的形式按元素（Global/Shadows/Midtones/Highlights）分组展示，模拟 DaVinci Resolve 等专业调色软件的工作流程。插件底层依赖 ObjectMixer 插件构建对象层级列表，通过 Data Model Generator 模式将不同 UObject 类型的色彩属性统一映射到同一个色轮界面。

值得注意的是，该插件标记为 `Hidden: true`，不会出现在插件浏览器中，但默认启用（`EnabledByDefault: true`），作为引擎内部 Color Grading 工作流的基础设施存在。

## 使用场景

- **影视虚拟制片（Virtual Production）**：你需要在编辑器中对场景的 PostProcessVolume 进行精细的色彩调整，使用色轮比在属性面板中手动输入 RGB 值更直观
- **摄像机色彩分级**：你正在使用 CineCameraActor 拍摄影片，需要快速调整白平衡、曝光补偿和色彩校正参数
- **多对象调色**：你需要同时对比和调整场景中多个后处理体积或摄像机的色彩设置
- **Multi-User 编辑**：在多人协作场景下，Color Grading 面板支持属性复制（replication）扩展

## 编辑器用法

### 打开 Color Grading 面板

Color Grading 面板作为 Nomad Tab 注册，可以通过以下方式打开：

1. **菜单路径**：Window → Color Grading
2. **快捷方式**：通过 `FColorGradingCommands` 注册的命令
3. **默认布局**：面板默认停靠在 Content Browser 所在的 Tab 组之前

### 面板结构

Color Grading 面板由以下部分组成：

| 区域 | 说明 |
|---|---|
| **对象列表**（左侧） | 基于 ObjectMixer 的场景对象层级，显示支持色彩分级的 Actor（PostProcessVolume、CameraActor、CineCameraActor） |
| **色轮面板**（右侧上方） | 5 个色轮：Saturation、Contrast、Gamma、Gain、Offset，每个色轮支持 RGB 和 HSV 两种显示模式 |
| **详情视图**（右侧下方） | 显示当前选中对象的附加属性，如 Exposure、White Balance、Color Grading 范围等 |

### 操作流程

1. 在对象列表中选择一个 PostProcessVolume 或 CameraActor
2. 色轮面板会自动更新，显示该对象的色彩分级元素（Global/Shadows/Midtones/Highlights）
3. 通过色轮调整各个元素的 Saturation、Contrast、Gamma、Gain、Offset
4. 详情视图可调整 Exposure 补偿、白平衡温度/色调、阴影/高光范围等附加参数
5. 支持 Undo/Redo 操作

### 色彩显示模式

色轮支持两种显示模式（通过 `UE::ColorGrading::EColorGradingColorDisplayMode` 控制）：
- **RGB 模式**：以 RGB 色彩空间显示色轮值
- **HSV 模式**：以 HSV 色彩空间显示色轮值

## C++ 用法

### 头文件引入

```cpp
#include "ColorGradingEditorDataModel.h"
#include "IColorGradingEditor.h"
#include "ColorGradingMixerObjectFilterRegistry.h"
#include "ColorGradingEditorUtil.h"
```

### 核心架构

#### Data Model（数据模型）

插件采用 Data Model + Generator 模式将不同 UObject 类型的色彩属性统一到一个抽象接口：

```cpp
// ColorGradingEditorDataModel.h
class FColorGradingEditorDataModel : public TSharedFromThis<FColorGradingEditorDataModel>
{
    // 色彩分级元素：包含 Saturation/Contrast/Gamma/Gain/Offset 五个属性句柄
    struct FColorGradingElement
    {
        FText DisplayName;
        TSharedPtr<IPropertyHandle> SaturationPropertyHandle;
        TSharedPtr<IPropertyHandle> ContrastPropertyHandle;
        TSharedPtr<IPropertyHandle> GammaPropertyHandle;
        TSharedPtr<IPropertyHandle> GainPropertyHandle;
        TSharedPtr<IPropertyHandle> OffsetPropertyHandle;
    };

    // 色彩分级组：包含多个元素（如 Shadows/Midtones/Highlights/Global）
    struct FColorGradingGroup
    {
        FText DisplayName;
        TArray<FColorGradingElement> ColorGradingElements;
        TArray<FName> DetailsViewCategories;
        bool bCanBeDeleted;
        bool bCanBeRenamed;
    };
};
```

#### Data Model Generator（数据模型生成器）

为不同 UObject 类型注册数据模型生成器：

```cpp
// IColorGradingEditorDataModelGenerator 接口
class IColorGradingEditorDataModelGenerator
{
    virtual void Initialize(const TSharedRef<FColorGradingEditorDataModel>& DataModel, const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) = 0;
    virtual void Destroy(const TSharedRef<FColorGradingEditorDataModel>& DataModel, const TSharedRef<IPropertyRowGenerator>& PropertyRowGenerator) = 0;
    virtual void GenerateDataModel(IPropertyRowGenerator& PropertyRowGenerator, FColorGradingEditorDataModel& OutDataModel) = 0;
};

// 注册方式（在模块启动时）
FColorGradingEditorDataModel::RegisterColorGradingDataModelGenerator<APostProcessVolume>(
    FGetDetailsDataModelGenerator::CreateStatic(&FColorGradingDataModelGenerator_PostProcessVolume::MakeInstance));

FColorGradingEditorDataModel::RegisterColorGradingDataModelGenerator<ACameraActor>(
    FGetDetailsDataModelGenerator::CreateStatic(&FColorGradingDataModelGenerator_CameraActor::MakeInstance));
```

#### 属性元数据映射

色彩属性通过 UPROPERTY 的 `ColorGradingMode` 元数据标记映射到色轮：

| 元数据值 | 映射到色轮 |
|---|---|
| `Saturation` | Saturation 色轮 |
| `Contrast` | Contrast 色轮 |
| `Gamma` | Gamma 色轮 |
| `Gain` | Gain 色轮 |
| `Offset` | Offset 色轮 |

### Object Filter Registry（对象过滤注册）

控制哪些对象类型出现在 Color Grading 面板的对象列表中：

```cpp
// 注册可显示的对象类
FColorGradingMixerObjectFilterRegistry::RegisterObjectClassToFilter(APostProcessVolume::StaticClass());
FColorGradingMixerObjectFilterRegistry::RegisterObjectClassToFilter(ACameraActor::StaticClass());

// 注册可放置的 Actor 类（通过面板的创建按钮）
FColorGradingMixerObjectFilterRegistry::RegisterActorClassToPlace(APostProcessVolume::StaticClass());
FColorGradingMixerObjectFilterRegistry::RegisterActorClassToPlace(ACineCameraActor::StaticClass());
FColorGradingMixerObjectFilterRegistry::RegisterActorClassToPlace(ACameraActor::StaticClass());
```

### 工具函数

```cpp
#include "ColorGradingEditorUtil.h"

// 创建一个按钮，点击后打开 Color Grading 面板
TSharedRef<SWidget> Button = ColorGradingEditorUtil::MakeColorGradingLaunchButton(true);
```

### 获取模块实例

```cpp
#include "IColorGradingEditor.h"

if (IColorGradingEditor::IsAvailable())
{
    IColorGradingEditor& ColorGradingEditor = IColorGradingEditor::Get();
    FName TabSpawnerId = ColorGradingEditor.GetColorGradingTabSpawnerId();
}
```

## 内部组件

### 模块结构

| 组件 | 路径 | 说明 |
|---|---|---|
| `FColorGradingEditorModule` | `Private/ColorGradingEditorModule.h/cpp` | 模块入口，注册菜单项和 Data Model Generator |
| `SColorGradingPanel` | `Public/SColorGradingPanel.h` | 主面板 Slate Widget，管理对象列表和色轮面板 |
| `SColorGradingColorWheelPanel` | `Private/SColorGradingColorWheelPanel.h/cpp` | 色轮面板，包含 5 个色轮和详情视图 |
| `SColorGradingColorWheel` | `Private/SColorGradingColorWheel.h/cpp` | 单个色轮 Widget |
| `FColorGradingEditorDataModel` | `Public/ColorGradingEditorDataModel.h` | 数据模型，存储色彩分级属性句柄 |
| `IColorGradingEditorDataModelGenerator` | `Public/ColorGradingEditorDataModel.h` | 数据模型生成器接口 |
| `FColorGradingDataModelGenerator_PostProcessVolume` | `Private/DataModelGenerators/` | PostProcessVolume 的数据模型生成器 |
| `FColorGradingDataModelGenerator_CameraActor` | `Private/DataModelGenerators/` | CameraActor 的数据模型生成器 |
| `UColorGradingMixerObjectFilter` | `Private/ColorGradingMixerObjectFilter.h` | ObjectMixer 对象过滤器实现 |
| `FColorGradingMixerObjectFilterRegistry` | `Public/ColorGradingMixerObjectFilterRegistry.h` | 对象类注册表 |
| `SColorGradingDetailView` | `Public/DetailView/SColorGradingDetailView.h` | 详情视图，显示附加属性 |
| `FColorGradingPanelState` | `Public/ColorGradingPanelState.h` | 面板状态持久化 |
| `FColorGradingCommands` | `Private/ColorGradingCommands.h` | UI 命令定义 |
| `ColorGradingEditorUtil` | `Public/ColorGradingEditorUtil.h` | 工具函数 |

### Camera Actor 特殊处理

CameraActor 的数据模型生成器对其 PostProcessSettings 做了额外处理，将以下属性分组显示在详情视图中：

| 类别 | 属性 |
|---|---|
| Exposure | AutoExposureBias |
| Color Grading | ColorCorrectionShadowsMax, ColorCorrectionHighlightsMin, ColorCorrectionHighlightsMax |
| White Balance | TemperatureType, WhiteTemp, WhiteTint |
| Misc | BlueCorrection, ExpandGamut, SceneColorTint |

Camera 组件的属性修改会自动创建事务（Transaction），支持 Undo/Redo。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AdvancedWidgets` | 高级 Slate Widget 组件 |
| `SceneOutliner` | 场景对象列表组件 |
| `ObjectMixerEditor` | 对象混合器编辑器，提供对象层级列表基础设施 |
| `CinematicCamera` | CineCameraActor 支持 |
| `DetailCustomizations` | 属性面板自定义 |
| `PropertyEditor` | 属性编辑器框架 |
| `LevelEditor` | 关卡编辑器集成（布局扩展） |
| `ToolMenus` | 工具菜单注册 |
| `ToolWidgets` | 工具 Widget 组件 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `9803c443cfab` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码现代化，添加内联生成宏 |
| 2025-05-30 | `8396b185774c` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types | API 导出宏规范化 |
| 2025-05-22 | `e6c5331579ae` | Color Grading x Multi User: Adjust behaviour of the "Add property to replication" property row extension button | Multi-User 编辑集成改进，调整属性复制按钮显示逻辑 |
| 2025-03-20 | `a2772a31b52f` | nDisplay: Fixed issue where color grading and white balance settings would reset to zero | nDisplay 集成修复，色彩分级和白平衡在数组元素中不再重置为零 |
| 2024-10-09 | `349c58cb7da6` | Fix crash when modifying a property where the outer object is null | 修复 Outer 对象为空时的崩溃问题 |

### 维护评价

- **创建时间**：2024-06-19，约 2 年前创建
- **活跃度**：活跃维护中，最近一次更新在 2025 年 7 月
- **更新内容**：包含功能增强（Multi-User 集成）、Bug 修复（nDisplay、崩溃修复）和代码质量改进
- **稳定性**：近期主要是维护性更新，核心功能已稳定
- **推荐**：✅ 推荐使用。该插件是 UE5 Color Grading 工作流的核心编辑器组件，默认启用且持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ColorGrading)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 依赖插件：[ObjectMixer](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ObjectMixer)
