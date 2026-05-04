# Gameplay Abilities Game Feature Actions

> Game feature actions to support modular use of the gameplay abilities system

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AbilitySystemGameFeatureActions (Runtime) |
| 创建时间 | 2021-06-22 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AbilitySystemGameFeatureActions) | |

## 用途

这个 plugin 为 UE5 的 **Game Feature** 系统提供了一个专用的 Action，用于在 Game Feature 插件注册或激活时向 **Gameplay Ability System (GAS)** 注册 **Attribute Default Tables**（属性默认值表）。

在 GAS 中，`UAbilitySystemGlobals` 管理着一个全局的属性默认值表列表，用于在初始化 `UAttributeSet` 时设置属性的初始值（如生命值上限、魔法值等）。通常这些表需要在游戏启动时通过 `DefaultAttributeSetDefaultsTableNames` 全局配置来设置。

但当你使用 Game Feature 系统做模块化设计时，某个 Game Feature 可能带来全新的 `AttributeSet`（比如一个 DLC 角色有自己独特的属性），这时就需要一个机制来**动态注册**对应的属性默认值表。

`AbilitySystemGameFeatureActions` 就是为了解决这个问题而存在的——它让 Game Feature 插件可以在注册/激活时自动向 `UAbilitySystemGlobals` 添加属性默认值表，并在卸载时自动清理，实现了属性默认值的**模块化管理**。

## 使用场景

- 你正在用 Game Feature 系统做模块化的 DLC / 角色 / 职业系统，每个 DLC/角色自带 `AttributeSet` → 用此 plugin 管理各自的属性默认值表
- 你需要在运行时动态加载/卸载属性默认值（如切换角色、切换 Game Feature 配置）→ `bApplyOnRegister` 控制时机
- 你想避免在主游戏配置中硬编码所有 DLC 的属性默认值 → 让每个 Game Feature 自带自己的默认值表

## 蓝图用法

此 plugin **没有暴露任何 BlueprintCallable 函数**。它完全通过编辑器配置使用。

### 核心节点

无蓝图节点。该 Action 是纯配置驱动的，通过 GameFeatureData 资产的 Actions 数组进行编辑器配置。

### 使用示例（编辑器配置）

1. 在你的 Game Feature 插件中创建或编辑 **GameFeatureData** 资产
2. 在该资产的 **Actions** 数组中，点击 **+** 添加一个新 Action
3. 在 Action 类型下拉菜单中选择 **"Add Attribute Defaults"**（即 `UGameFeatureAction_AddAttributeDefaults`）
4. 配置以下属性：
   - **AttribDefaultTableNames**：添加你的属性默认值表的资产路径（`TArray<FSoftObjectPath>`），例如 `/Game/Data/DT_MyCharacterAttributeDefaults`
   - **bApplyOnRegister**（高级选项）：
     - `true`（默认）：Game Feature 插件注册时立即应用属性默认值
     - `false`：等 Game Feature 插件激活时才应用属性默认值

## C++ 用法

此 plugin 不提供 C++ 扩展 API。它是 GameFeatureAction 系统的一个具体实现，通过 GameFeatureData 资产配置使用。

如果你需要在自定义代码中做类似的事情，可以直接调用 `UAbilitySystemGlobals` 的 API：

### 头文件引入

```cpp
#include "AbilitySystemGlobals.h"
```

### 基本用法

以下代码展示了 `UGameFeatureAction_AddAttributeDefaults` 内部实际做的事情（参考源码 `GameFeatureAction_AddAttributeDefaults.cpp`）：

```cpp
// 向 UAbilitySystemGlobals 注册属性默认值表
UAbilitySystemGlobals& AbilitySystemGlobals = UAbilitySystemGlobals::Get();

TArray<FSoftObjectPath> TableNames;
TableNames.Add(FSoftObjectPath(TEXT("/Game/Data/DT_CharacterDefaults")));

// 以某个 Owner 名称注册，便于后续按 Owner 移除
AbilitySystemGlobals.AddAttributeDefaultTables(FName(TEXT("MyOwner")), TableNames);
```

### 进阶用法

在 Game Feature 的生命周期中管理属性默认值的注册与清理：

```cpp
// 注册时添加
void OnFeatureRegistering()
{
    UAbilitySystemGlobals& ASG = UAbilitySystemGlobals::Get();
    ASG.AddAttributeDefaultTables(OwnerName, AttribDefaultTableNames);
}

// 反注册时移除（清理硬引用，避免内存泄漏）
void OnFeatureUnregistering()
{
    UAbilitySystemGlobals& ASG = UAbilitySystemGlobals::Get();
    ASG.RemoveAttributeDefaultTables(OwnerName, AttribDefaultTableNames);
}
```

注意：移除行为受 CVar `GameFeatureAction_AddAttributeDefaults.AllowRemoveAttributeDefaultTables` 控制（默认 `true`），可在运行时通过控制台修改。

## 模块依赖

从 `Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 | 类型 |
|---|---|---|
| `Core` | UE 核心库 | Public |
| `CoreUObject` | UObject 系统 | Public |
| `DeveloperSettings` | 开发者设置基类 | Public |
| `Engine` | 引擎核心 | Public |
| `ModularGameplay` | 模块化 Gameplay 组件系统 | Public |
| `DataRegistry` | 数据注册表系统 | Public |
| `GameFeatures` | Game Feature 插件系统（提供 `UGameFeatureAction` 基类） | Private |
| `GameplayAbilities` | GAS 能力系统（提供 `UAbilitySystemGlobals`） | Private |

此外，plugin 级别声明了依赖：
- **GameFeatures** plugin
- **GameplayAbilities** plugin

要在你的项目中使用此 plugin，确保项目的 `.Build.cs` 中依赖了 `GameplayAbilities` 和 `GameFeatures` 模块。

## Demo 示例

此 plugin 不提供可编译的 C++ Demo——它通过配置即用。以下是一个完整的 GameFeatureData 配置示例：

### 场景：为一个 DLC 角色添加自定义属性默认值

**1. 准备属性默认值数据表**

创建一个 DataTable 资产（行结构为 `FAttributeMetaData`），定义你的属性默认值：

| AttributeName | BaseValue | AttributeOwner |
|---|---|---|
| Health | 100.0 | /Script/MyGame.MyAttributeSet |
| Mana | 50.0 | /Script/MyGame.MyAttributeSet |
| Shield | 25.0 | /Script/MyGame.MyAttributeSet |

保存为 `/Game/DLC/DT_DLCCharacterDefaults`。

**2. 配置 GameFeatureData**

在你的 Game Feature 插件的 Content 目录下创建 `GameFeatureData` 资产，在 Actions 中添加：

```
Action[0]:
  Class: GameFeatureAction_AddAttributeDefaults (Add Attribute Defaults)
  AttribDefaultTableNames:
    [0]: /Game/DLC/DT_DLCCharacterDefaults
  bApplyOnRegister: true  (默认值)
```

**3. 效果**

- 当你的 Game Feature 插件被**注册**时（通常是引擎启动时扫描到该插件），`DT_DLCCharacterDefaults` 会被添加到 `UAbilitySystemGlobals` 的全局属性默认值表列表中
- 当 Game Feature 插件被**反注册**时，对应的表会被自动移除
- `UAttributeSet` 在初始化时会读取这些默认值表来设置属性初始值

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2024-11-09 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 全局代码清理，移除 UE 5.2 弃用的头文件包含顺序兼容宏，非功能性变更 |
| 2024-05-29 | `898df968` | Added toggle to apply attribute set defaults in OnGameFeatureActivating | **功能性更新**：新增 `bApplyOnRegister` 属性，允许选择在注册时还是激活时应用默认值。之前只能在注册时应用 |
| 2024-01-29 | `92cb46cb` | Fix GameFeatureAction_AddAttributeDefaults not cleaning up references to objects when unregistered | Bug 修复：修复了反注册时未清理属性默认值表引用的问题，避免内存泄漏 |

### 维护评价

- **年龄**：约 4.9 年（2021-06 创建），仍属 🆕 范围
- **维护状态**：**维护中**——最近一次功能性更新在 2024-05，最近一次提交在 2024-11
- **状态标签**：Experimental / IsBetaVersion = true / EnabledByDefault = false，属于实验性插件
- **代码质量**：代码简洁（仅 1 个 Action 类，约 210 行源码），逻辑清晰
- **已知限制**：
  - 仍标记为 Beta，API 可能在未来版本发生变化
  - 没有官方文档（DocsURL 为空）
  - 没有测试用例
  - 源码仅有 3 个 .cpp/.h 文件，功能单一
- **推荐程度**：如果你正在使用 Game Feature 系统做模块化 Gameplay Ability 设计，推荐使用。但要注意它仍是实验性的，升级引擎版本时需检查兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AbilitySystemGameFeatureActions)
- [UGameFeatureAction 基类源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GameFeatures/Source/GameFeatures/Public/GameFeatureAction.h)
- [UAbilitySystemGlobals 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GameplayAbilities/Source/GameplayAbilities/Public/AbilitySystemGlobals.h)
