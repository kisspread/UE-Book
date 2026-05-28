# Composure — Legacy Composure Layers Editor

> Legacy system for real-time compositing. This plugin is no longer developed. Use Composure going forward.

| 属性 | 值 |
|---|---|
| 中文名 | 合成层编辑器 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 Slate UI 样式与图标资源） |
| 模块 | `Composure` (Runtime), `ComposureEditor` (Runtime), `ComposureLayersEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure) | |

---

## 用途

Composure 是 Unreal Engine 的**实时合成（Real-Time Compositing）**插件，专为虚拟制片（Virtual Production）工作流设计。它允许用户在引擎内将 CG 元素与实时画面进行合成，而无需导出到外部合成软件（如 Nuke、After Effects）。

**本文档覆盖的 `ComposureLayersEditor` 模块**是该插件的**编辑器 UI 层**，提供了在虚幻编辑器中管理和操作合成元素（Compositing Element）的完整界面，包括：

- **合成元素树浏览器**：以树形结构展示所有合成元素的层级关系
- **元素管理接口**（`ICompElementManager`）：创建、删除、重命名、挂载合成元素的统一 API
- **实时预览窗口**：独立窗口显示单个合成元素的渲染结果
- **颜色拾取器**：从合成预览画面中拾取颜色值
- **属性面板自定义**：为合成材质通道提供专用的属性编辑 UI
- **媒体捕获管理**：控制将合成结果输出到媒体设备（如 SDI 输出）

该插件标记为 **Legacy**（已废弃），`EnabledByDefault=false`。源码描述明确指出"Use Composure going forward"，建议在新项目中使用更新版本的合成系统。

---

## 使用场景

- 你需要在虚幻编辑器中**将多个 CG 图层合成为最终画面** → 使用 Composure Elements 配置输入源和效果
- 你在做**虚拟制片（Virtual Production）**，需要实时合成 LED 墙画面与前景 CG → 用 Composure 管理各图层
- 你需要**将合成结果输出到 SDI/HDMI 设备**（如广播级硬件输出） → 用媒体捕获输出通道
- 你需要在编辑器中**预览单个合成元素的渲染结果** → 用合成预览窗口
- 你需要在蓝图或 C++ 中**程序化创建和管理合成元素** → 用 `ICompElementManager` 接口

---

## 核心接口与 API

### ICompElementManager

合成元素管理的核心接口，定义在 `Public/ICompElementManager.h`。通过 `ICompElementEditorModule::GetCompElementManager()` 获取实例。

#### 元素 CRUD 操作

| 函数 | 说明 |
|---|---|
| `CreateElement` | 创建新的合成元素 Actor，可指定类类型、层级上下文和对象标志 |
| `GetElement` | 根据名称获取已存在的合成元素 |
| `TryGetElement` | 尝试获取元素，返回 bool 表示是否成功（安全版本） |
| `AddAllCompElementsTo` | 将所有已知元素添加到输出数组 |
| `DeleteElementAndChildren` | 删除指定元素及其所有子元素 |
| `DeleteElements` | 批量删除多个元素及其子元素 |
| `RenameElement` | 重命名元素 |
| `AttachCompElement` | 将元素挂载为另一个元素的子节点 |

#### 元素状态控制

| 函数 | 说明 |
|---|---|
| `ToggleElementRendering` | 切换元素的渲染启用/禁用状态 |
| `ToggleElementFreezeFrame` | 切换元素的冻结帧状态 |
| `ToggleMediaCapture` | 添加/启用/禁用媒体捕获输出通道 |
| `ResetMediaCapture` | 重新选择媒体输出目标资产 |
| `RemoveMediaCapture` | 删除元素上的所有媒体捕获通道 |

#### 编辑器交互

| 函数 | 说明 |
|---|---|
| `SelectElementActors` | 在编辑器中选中/取消选中指定的合成元素 Actor |
| `RefreshElementsList` | 重新扫描场景中的元素 Actor 并重建列表 |
| `RequestRedraw` | 请求编辑器重绘合成画面 |
| `IsDrawing` | 查询指定元素是否正在被渲染 |

#### 回调与事件

| 事件 | 说明 |
|---|---|
| `OnElementsChanged` | 元素被修改时广播（添加/修改/删除/重命名/重置） |
| `OnCreateNewElement` | 新元素通过蓝图/C++ 创建后的回调 |
| `OnDeleteElement` | 元素被删除前的回调 |

### ECompElementEdActions 枚举

```cpp
enum class ECompElementEdActions
{
    Add,
    Modify,
    Delete,
    Rename,
    Reset
};
```

---

### ICompElementEditorModule

模块入口接口，定义在 `Public/CompElementEditorModule.h`。

```cpp
class ICompElementEditorModule : public IModuleInterface
{
public:
    static ICompElementEditorModule& Get();
    virtual TSharedPtr<ICompElementManager> GetCompElementManager() = 0;
    virtual TArray<FCompEditorMenuExtender>& GetEditorMenuExtendersList() = 0;
};
```

| 函数 | 说明 |
|---|---|
| `Get()` | 获取模块单例 |
| `GetCompElementManager()` | 获取合成元素管理器实例 |
| `GetEditorMenuExtendersList()` | 获取可扩展编辑器菜单的委托列表 |

---

## 属性面板自定义

### FCompElementDetailsCustomization

为 `ACompositingElement` 的 Details 面板提供自定义布局，处理相机源选择等特殊属性。

### FCompositingMaterialPassCustomization

为 `FCompositingMaterial` 结构体提供自定义属性编辑 UI，包括：

- **材质参数覆盖**：Scalar、Vector、Texture 类型参数的自定义编辑控件
- **参数源选择**：下拉菜单选择参数来源（其他合成元素的输出）
- **通道选择**：自动构建可用的元素通道名称列表
- **撤销/重做支持**：继承 `FEditorUndoClient`

### FCompositingPassCustomization

为合成通道属性提供通用的自定义，包括实例对象句柄处理和预览按钮创建。

---

## 蓝图用法

本模块主要是编辑器内部 UI 模块，不直接暴露蓝图可调用函数。但通过 `ICompElementManager` 接口管理的 `ACompositingElement` Actor 在蓝图中可直接使用。

### 核心节点（通过 Composure 主模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateElement` | 创建新的合成元素 | `ICompElementManager` |
| `GetElement` / `TryGetElement` | 获取已存在的合成元素 | `ICompElementManager` |
| `ToggleElementRendering` | 启用/禁用元素渲染 | `ICompElementManager` |
| `ToggleMediaCapture` | 管理媒体捕获输出 | `ICompElementManager` |

### 使用示例（蓝图描述）

**创建并预览合成元素：**
1. 在编辑器中打开 Composure 面板（Window → Composure）
2. 右键空白区域 → 选择 "Create New Comp"
3. 选择元素类类型（如 CgCaptureCompElement）
4. 在 Details 面板中配置输入源和材质通道
5. 双击元素或按 `P` 键打开预览窗口

**媒体捕获输出：**
1. 选中目标合成元素
2. 在元素行右键 → Toggle Media Capture
3. 选择 `UMediaOutput` 资产
4. 元素渲染结果将实时输出到指定媒体设备

---

## C++ 用法

### 头文件引入

```cpp
#include "CompElementEditorModule.h"
```

### 基本用法

从模块接口获取元素管理器并执行操作：

```cpp
// 获取 Composure 编辑器模块
ICompElementEditorModule& ComposureModule = ICompElementEditorModule::Get();
TSharedPtr<ICompElementManager> ElementManager = ComposureModule.GetCompElementManager();

if (ElementManager.IsValid())
{
    // 创建一个新的合成元素
    TWeakObjectPtr<ACompositingElement> NewElement = ElementManager->CreateElement(
        FName("MyNewElement"),
        ACompositingElement::StaticClass()
    );

    // 获取已有元素
    TWeakObjectPtr<ACompositingElement> ExistingElement;
    if (ElementManager->TryGetElement(FName("MyNewElement"), ExistingElement))
    {
        // 元素存在，可以操作
    }

    // 切换渲染状态
    ElementManager->ToggleElementRendering(FName("MyNewElement"));

    // 删除元素及其子元素
    ElementManager->DeleteElementAndChildren(FName("MyNewElement"));
}
```

### 进阶用法

监听元素变化事件并响应：

```cpp
#include "CompElementEditorModule.h"

class FMyComposureListener
{
public:
    void Initialize()
    {
        ICompElementEditorModule& Module = ICompElementEditorModule::Get();
        TSharedPtr<ICompElementManager> Manager = Module.GetCompElementManager();

        if (Manager.IsValid())
        {
            // 绑定元素变化事件
            Manager->OnElementsChanged().AddRaw(this, &FMyComposureListener::OnElementsChanged);
        }
    }

    void Cleanup()
    {
        ICompElementEditorModule& Module = ICompElementEditorModule::Get();
        TSharedPtr<ICompElementManager> Manager = Module.GetCompElementManager();

        if (Manager.IsValid())
        {
            Manager->OnElementsChanged().RemoveAll(this);
        }
    }

private:
    void OnElementsChanged(
        const ECompElementEdActions Action,
        const TWeakObjectPtr<ACompositingElement>& ElementObj,
        const FName& ChangedProperty)
    {
        switch (Action)
        {
        case ECompElementEdActions::Add:
            UE_LOG(LogTemp, Log, TEXT("Element added: %s"), *ElementObj->GetName());
            break;
        case ECompElementEdActions::Delete:
            UE_LOG(LogTemp, Log, TEXT("Element deleted: %s"), *ChangedProperty.ToString());
            break;
        case ECompElementEdActions::Rename:
            UE_LOG(LogTemp, Log, TEXT("Element renamed, new name: %s"), *ChangedProperty.ToString());
            break;
        // ... 处理其他操作类型
        }
    }
};
```

---

## 模块依赖

由于未提供 `ComposureLayersEditor.Build.cs` 源码，以下依赖从代码分析推断：

| 模块 | 用途 |
|---|---|
| `Composure` | 核心合成系统（`ACompositingElement` 等运行时类） |
| `LevelEditor` | 编辑器关卡操作、Actor 选择同步 |
| `PropertyEditor` | 属性面板自定义（`IDetailCustomization`、`IPropertyTypeCustomization`） |
| `ToolMenus` | 编辑器菜单扩展 |
| `InputCore` | 快捷键输入（`EKeys`） |

无特殊依赖（仅标准 Core/Engine/Slate/Editor 等）

---

## 模块内部架构

### 类层次关系

```
ICompElementEditorModule (模块入口)
  └── ICompElementManager (核心接口)
        └── FCompElementManager (实现，FGCObject)
              └── UEditorCompElementContainer (UObject，Undo/Redo 支持)

FCompElementCollectionViewModel (集合视图模型)
  └── FCompElementViewModel (单元素视图模型)

SCompElementBrowser (主浏览器面板)
  └── SCompElementsView (树形列表视图)
        └── SCompElementViewRow (行渲染)

SCompElementPreviewPane (预览面板)
SCompElementPreviewDialog (预览对话框窗口)
SCompElementPickerWindow (颜色拾取窗口)
```

### Slate 控件一览

| 控件 | 说明 |
|---|---|
| `SCompElementBrowser` | 顶层浏览器面板，包含搜索框和元素树 |
| `SCompElementsView` | 树形列表视图，支持拖放、多选 |
| `SCompElementViewRow` | 单行渲染，含可见性开关、冻结帧、媒体捕获状态、Alpha 滑块 |
| `SCompElementPreviewPane` | 预览面板，支持通道查看（R/G/B/A）、颜色拾取 |
| `SCompElementPreviewDialog` | 独立预览窗口 |
| `SCompElementPickerWindow` | 颜色拾取对话框 |
| `SCompElementEdCommandsMenu` | 右键上下文菜单 |

### 快捷键

| 快捷键 | 功能 |
|---|---|
| `F5` | 刷新合成元素列表 |
| `P` | 打开选中元素的预览窗口 |
| `C` | 重置颜色拾取器 |
| `F` | 切换冻结帧 |
| `R` | 查看红色通道 |
| `G` | 查看绿色通道 |
| `B` | 查看蓝色通道 |
| `A` | 查看 Alpha 通道 |
| `Tab` | 循环切换通道预设 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联通知机制 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退 CL53913857 的改动 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联通知重构（重新提交） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-04-13 | `efbf4c0b` | Viewport: Use managed pointer for reference to Client | 视口改用智能指针管理客户端引用 |

### 维护评价

⚠️ **此插件已被标记为 Legacy（已废弃）**。`.uplugin` Description 明确说明"This plugin is no longer developed. Use Composure going forward"。

- **创建时间**：2017 年 6 月，已存在约 8 年
- **默认启用**：`EnabledByDefault=false`，需要手动在插件设置中启用
- **近期活动**：最近的提交（2026 年 5 月）均为引擎级重构（视口机制、日志迁移），并非功能更新或 bug 修复
- **实质性更新**：最近的实质性功能更新可能追溯到更早时期。近 6 个月的改动都是引擎底层基础设施的附带修改，非本插件主动维护
- **推荐**：**不推荐在新项目中使用**。此版本为遗留系统，Epic 建议使用更新的 Composure 系统。如果你在维护使用此旧版本的项目，它仍然可以工作，但不会再获得新功能

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure)
- 官方文档（无，`.uplugin` 中 DocsURL 为空）