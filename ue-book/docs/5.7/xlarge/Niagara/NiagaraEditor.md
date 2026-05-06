# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 粒子编辑器 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资产、细节面板、自定义节点、模拟缓存查看器等） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara) | |

---

## 用途

**NiagaraEditor** 是 Niagara 粒子系统的编辑器模块，负责在 Unreal Editor 中提供全套可视化编辑工具。它解决了以下问题：

- 使美术与设计师无需编写代码即可创建复杂的粒子/特效（VFX）
- 提供节点式图表（系统蓝图、模块蓝图）与堆栈面板，支持快速迭代
- 集成模拟缓存、调试、平台配置、参数绑定等高级编辑功能
- 注册并管理所有 Niagara 相关资产类型（系统、发射器、脚本、参数集合等）

---

## 使用场景

- 你需要为游戏创建火焰、爆炸、烟雾、魔法等实时粒子特效 → 安装 Niagara 插件并使用 `NiagaraSystem` 资产
- 你想在 C++ 或蓝图中动态创建/修改 Niagara 组件 → 使用 `UNiagaraComponent` 配合 NiagaraEditor 预览
- 需要调试粒子性能或查看内部状态 → 使用 Niagara Outliner 和 Debug HUD（由该模块提供）
- 需要为自定义数据接口（Data Interface）添加编辑器支持 → 继承 `FNiagaraDataInterfaceSimCacheVisualizer` 或实现自定义细节面板

---

## 蓝图用法

**说明**：`NiagaraEditor` 模块本身主要为编辑器提供工具，不直接暴露蓝图可调用的节点。Niagara 的蓝图节点位于 `NiagaraBlueprintNodes` 模块（如 `Spawn Niagara System`、`Set Niagara Variable` 等）。  
在编辑器中，以下操作可通过蓝图编辑器内调用相关函数实现（需要运行时模块支持）：

### 常见编辑器辅助函数（通过 `UNiagaraEditorSubsystem` 暴露）

| 节点（或函数） | 说明 | 所在类 |
|---|---|---|
| `GetNiagaraEditorSubsystem` | 获取编辑器内 Niagara 子系统 | `UNiagaraEditorSubsystem` |
| `GetActiveNiagaraSystems` | 返回当前世界中所有活跃的 Niagara 系统实例 | `UNiagaraEditorSubsystem` |
| `SpawnPreviewSystem` | 在编辑器中生成预览系统 | `UNiagaraEditorSubsystem` |

> 注：大部分编辑器交互（如打开系统、启动模拟）通过菜单和资产操作触发，无需蓝图。

---

## C++ 用法

### 头文件引入

```cpp
#include "Engine/NiagaraComponent.h"
#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraDataInterface.h"
// 编辑器模块
#include "NiagaraEditorModule.h"
#include "ViewModels/Stack/NiagaraStackEntry.h"
#include "Customizations/NiagaraParameterBindingAdapter.h"
```

### 基本用法

```cpp
// 在模块启动时注册自定义数据接口的模拟缓存可视化器
#include "NiagaraEditorModule.h"
#include "Customizations/NiagaraDataInterfaceSimCacheVisualizer.h"

void RegisterMySimCacheVisualizer()
{
    FNiagaraEditorModule& NiagaraEditorModule = FModuleManager::LoadModuleChecked<FNiagaraEditorModule>("NiagaraEditor");
    NiagaraEditorModule.RegisterSimCacheVisualizer(MyDataInterfaceClass, []() -> TSharedPtr<INiagaraDataInterfaceSimCacheVisualizer>
    {
        return MakeShared<FMySimCacheVisualizer>();
    });
}
```

```cpp
// 创建自定义参数绑定适配器（参考 FNiagaraParameterBindingAdapter）
class FMyBindingAdapter : public FNiagaraParameterBindingAdapter
{
public:
    virtual bool IsSetToParameter() const override { return !ResolvedParameterName.IsNone(); }
    virtual bool AllowConstantValue() const override { return true; }
    virtual FNiagaraTypeDefinition GetConstantTypeDef() const override { return FNiagaraTypeDefinition::GetFloatDef(); }
    virtual TConstArrayView<uint8> GetConstantValue() const override { /*...*/ }
    virtual void SetConstantValue(TConstArrayView<uint8> Memory) const override { /*...*/ }
    virtual const FNiagaraVariableBase& GetBoundParameter() const override { return BoundParameter; }
    virtual void SetBoundParameter(const FInstancedStruct& Parameter) override { /*...*/ }
    virtual bool IsSetToDefault() const override { return false; }
    virtual void SetToDefault() override { /*...*/ }
    virtual void CollectBindings(...) const override { /*...*/ }
};
// 然后注册到 FNiagaraParameterBindingAdapterCustomization
```

### 进阶用法

```cpp
// 使用 NiagaraStackQuery 在编辑器模块内查找特定堆栈条目
#include "NiagaraStackQuery.h"

void FindInputInEmitterStack(UNiagaraEmitter* Emitter, FName InputName)
{
    // 假设已获得 StackRoot 等结构
    // 使用 FNiagaraStackModuleItemQuery 等递归查询
    FNiagaraStackModuleItemQuery ModuleQuery(/*...*/);
    auto InputQuery = ModuleQuery.FindFunctionInput(InputName);
    if (InputQuery.IsValid())
    {
        UNiagaraStackFunctionInput* Input = InputQuery.GetResult().StackEntry;
        // 修改输入值
    }
}
```

```cpp
// 访问 Niagara Stateless Emitter 模板并生成计算 HLSL
#include "ViewModels/NiagaraStatelessEmitterTemplateViewModel.h"

void GenerateShaderCode(UNiagaraStatelessEmitterTemplate* Template)
{
    FNiagaraStatelessEmitterTemplateViewModel ViewModel(Template);
    FString HLSLCode = ViewModel.GenerateComputeTemplateHLSL();
    // 保存或检查 HLSL
}
```

---

## Demo 示例

以下是一个完整的 C++ 示例，在编辑器内注册一个自定义资产类型对应的资产定义（简化版本）。

**MyAssetDefinition_NiagaraCustom.h**

```cpp
#pragma once

#include "AssetDefinitionDefault.h"
#include "MyAssetDefinition_NiagaraCustom.generated.h"

UCLASS()
class UMyAssetDefinition_NiagaraCustom : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    virtual FText GetAssetDisplayName() const override { return NSLOCTEXT("AssetTypeActions", "NiagaraCustom", "Niagara Custom"); }
    virtual FLinearColor GetAssetColor() const override { return FLinearColor::White; }
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override
    {
        static const auto Categories = { EAssetCategoryPaths::FX / NSLOCTEXT("Niagara", "NiagaraAssetSubMenu_Advanced", "Advanced") };
        return Categories;
    }
};
```

**MyAssetDefinition_NiagaraCustom.cpp**

```cpp
#include "MyAssetDefinition_NiagaraCustom.h"
#include "MyCustomNiagaraAsset.h" // 假设的自定义资产类

TSoftClassPtr<UObject> UMyAssetDefinition_NiagaraCustom::GetAssetClass() const
{
    return UMyCustomNiagaraAsset::StaticClass();
}
```

然后在模块的 `StartupModule` 中注册该资产定义。

---

## 模块依赖

**备注**：`NiagaraEditor` 本身是编辑器模块，依赖众多引擎模块。以下列出其独特的、非标准的依赖关系。常见的 Core/Engine/Slate 等已省略。

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心运行时类型（系统、发射器、脚本等） |
| `NiagaraCore` | 基础参数、变量类型定义 |
| `NiagaraShader` | 着色器编译与参数映射 |
| `NiagaraVertexFactories` | 顶点工厂与渲染 |
| `AdvancedPreviewScene` | 编辑器预览场景 |
| `PropertyEditor` | 属性细节面板定制（虽常见但此处为主动依赖） |
| `AssetDefinition` | 资产定义注册框架 |
| `WorkspaceMenuStructure` | 编辑器菜单结构 |
| `PythonScriptPlugin` | Python 脚本支持（可选依赖） |

**你的模块如果需要使用 `NiagaraEditor` 的功能，请在 `Build.cs` 的 `PublicDependencyModuleNames` 中添加：**

```cpp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Niagara",
    "NiagaraEditor",
    "NiagaraCore",
    "NiagaraShader",
    "PropertyEditor",
    "AssetDefinition"
});
```

---

## 维护状态

### 近期更新

- 2025-10-22 `5d0cd83c` — Fix for issue with access to freed Niagara Components during cleanup.
- 2025-10-22 `3f549682` — Fixed issue with lingering NDC data when there are updates with no data from the CPU.
- 2025-10-21 `6ac05a79` — Added off-by-default workaround for Niagara crash we hit in internal testing.
- 2025-10-17 `f6546371` — Fix issue caused by mis-matched GT and RT ticks causing NDC data to be effectively lost from the POV.
- 2025-10-16 `566219ca` — [Backout] - CL47013072

### 维护评价

- **创建时间**：2025-10-16（基于 git log 最早记录），但实际插件历史较长，此日期代表近期重大重构/版本更新。
- **近期更新**：全部为 2025 年 10 月的 bug 修复，频率密集（几乎每天 1-2 个 commit），说明团队正在积极维护。
- **活跃度**：当前处于活跃维护状态，修复集中在稳定性（组件释放、数据竞争、渲染同步）上。
- **推荐使用**：作为 UE5 的默认粒子系统编辑器，强烈推荐使用。注意及时更新到最新版本以获得修复。

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/niagara-overview/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Tests)