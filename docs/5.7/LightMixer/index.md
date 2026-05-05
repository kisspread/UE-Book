# Light Mixer

> Edit any properties of scene lights in a spreadsheet format!

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | true |
| 包含内容 | true |
| 模块 | LightMixer (Editor) |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/ObjectMixer/LightMixer) | |

## 用途

Light Mixer 是 ObjectMixer 的一个特化子插件（sub-plugin），专门用于以电子表格的方式批量编辑场景中的灯光属性。

它的核心机制非常简单：继承 `UObjectMixerObjectFilter`，将过滤范围限定为 `ULightComponent`（组件级）和 `ALight`（Actor 级），然后通过 ObjectMixer 的表格 UI 暴露灯光的可编辑属性。默认显示的列包括 **Intensity**（强度）、**LightColor**（灯光颜色）、**LightingChannels**（光照通道）和 **AttenuationRadius**（衰减半径），同时通过 `ForceAddedColumns` 确保 LightColor 和 LightingChannels 始终可见。

简单来说，Light Mixer = ObjectMixer + 灯光过滤器。它让美术和灯光师可以在一个统一的表格界面中快速调整大量灯光，而不需要逐个选择并修改每个灯光 Actor 的 Details 面板。

## 使用场景

- 你在做关卡灯光调整，需要同时修改 50+ 个点光源的强度和颜色 → 用 Light Mixer 打开表格，批量编辑 Intensity 和 LightColor 列
- 你需要快速找到场景中哪些灯光使用了特定的光照通道 → 用 Light Mixer 的 LightingChannels 列排序筛选
- 你需要对比所有灯光的衰减半径并统一调整 → 在 AttenuationRadius 列中直接对比和修改
- 你希望在 Light Mixer 中隐藏原始的 ObjectMixer 菜单项以减少 UI 混乱 → 在 Editor > Plugins > Light Mixer 设置中启用 `bHideObjectMixerMenuItem`

## 蓝图用法

Light Mixer 是纯编辑器 UI 模块，不提供蓝图节点或 BlueprintCallable 函数。它的所有功能通过编辑器菜单栏的 **Light Mixer** 面板访问。

## C++ 用法

Light Mixer 没有对外暴露公共 C++ API。它是一个完全自包含的编辑器模块，不设计为被其他模块依赖。

如果你需要在自己的插件中实现类似的"表格编辑特定类型对象"功能，应该直接使用 ObjectMixer 的基类 `UObjectMixerObjectFilter`，参考 Light Mixer 的实现模式：

### 核心代码模式

Light Mixer 的全部逻辑都在 `ULightMixerObjectFilter` 中（来源: `Source/LightMixer/Public/LightMixerObjectFilter.h`）：

```cpp
UCLASS(MinimalAPI, BlueprintType, EditInlineNew)
class ULightMixerObjectFilter : public UObjectMixerObjectFilter
{
    GENERATED_BODY()
public:
    // 1. 指定要过滤的组件类型
    virtual TSet<UClass*> GetObjectClassesToFilter() const override
    {
        return { ULightComponent::StaticClass() };
    }

    // 2. 指定要在表格中放置/创建的 Actor 类型
    virtual TSet<TSubclassOf<AActor>> GetObjectClassesToPlace() const override
    {
        return { ALight::StaticClass() };
    }

    // 3. 显示临时对象（如预览灯光）
    virtual bool GetShowTransientObjects() const override
    {
        return true;
    }

    // 4. 默认显示的属性列
    virtual TSet<FName> GetColumnsToShowByDefault() const override
    {
        return { "Intensity", "LightColor", "LightingChannels", "AttenuationRadius" };
    }

    // 5. 强制显示的列（用户不可隐藏）
    virtual TSet<FName> GetForceAddedColumns() const override
    {
        return { "LightColor", "LightingChannels" };
    }

    // 6. 属性继承选项：包含所有父类和子类的属性
    virtual EObjectMixerInheritanceInclusionOptions
        GetObjectMixerPropertyInheritanceInclusionOptions() const override
    {
        return EObjectMixerInheritanceInclusionOptions::IncludeAllParentsAndChildren;
    }

    // 7. 放置类继承选项：包含所有子类（如 SpotLight、PointLight 等）
    virtual EObjectMixerInheritanceInclusionOptions
        GetObjectMixerPlacementClassInclusionOptions() const override
    {
        return EObjectMixerInheritanceInclusionOptions::IncludeAllChildren;
    }
};
```

## Demo 示例

Light Mixer 不需要编写代码使用。启用插件后：

1. 打开 UE5 编辑器
2. 在菜单栏找到 **Light Mixer**（通常在 Window 菜单下）
3. 点击打开 Light Mixer 面板
4. 面板会自动列出当前关卡中的所有灯光 Actor
5. 在表格中直接编辑 Intensity、LightColor 等属性
6. 支持多选批量编辑

### 隐藏 ObjectMixer 菜单项

如果你只想使用 Light Mixer 而不想看到通用的 Object Mixer 菜单：

1. 打开 **Editor > Plugins > Light Mixer** 设置
2. 勾选 **Hide Object Mixer Menu Item**
3. 重启编辑器生效

## 模块依赖

从 `LightMixer.build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `OutputLog` | 输出日志功能 |
| `ObjectMixerEditor` | 父插件 ObjectMixer 的编辑器模块，提供表格 UI 基础设施 |
| `PropertyEditor` | 属性编辑器基础设施 |

私有依赖（不需要直接引用）：AssetRegistry, AssetTools, CoreUObject, ContentBrowser, Engine, EditorStyle, EditorWidgets, InputCore, Kismet, Projects, Slate, SlateCore, ToolMenus, ToolWidgets, UnrealEd, WorkspaceMenuStructure

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-05-30 | `8396b18` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 2/n |
| 2023-05-11 | `91c57d3` | Removed redundant module includes. |
| 2023-04-25 | `92bfef0` | Object Mixer: (commit message truncated) |

解读：最近一次实质性更新是 2023-05-11 的清理工作（移除冗余 include）。2025-05-30 的更新是全引擎范围的 DLL export 修复，不涉及功能变更。该插件自 2022 年创建以来代码量极小（6 个源文件），功能稳定，基本不需要频繁更新。

### 维护评价

- **年龄**: 创建于 2022-08-23，约 3.7 年
- **状态**: 标记为 `IsBetaVersion = true`，`Hidden = true`（在插件浏览器中默认隐藏）
- **代码规模**: 极小（6 个 .h/.cpp 文件），核心逻辑仅一个 Filter 类
- **最近更新**: 2025-05 有编译修复，但无功能性更新已超过 2 年
- **结论**: 作为 ObjectMixer 的轻量级特化插件，功能简单且稳定。虽然是 Beta 状态且默认隐藏，但默认启用且稳定可用。适合需要批量灯光编辑的场景使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/ObjectMixer/LightMixer)
- [父插件 ObjectMixer 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/ObjectMixer/ObjectMixer)
- 官方文档: 无（.uplugin 中 DocsURL 为空）
