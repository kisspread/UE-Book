# CLion Integration

> Allows access to source code in CLion.

| 属性 | 值 |
|---|---|
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 否 |
| 模块 | CLionSourceCodeAccess (UncookedOnly) |
| 创建时间 | 2017-12-07 |
| 年龄标签 | 👴 老古董（~8.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/Developer/CLionSourceCodeAccess) | |

## 用途

这个 plugin 是 UE5 编辑器与 JetBrains CLion IDE 之间的**源码访问桥接器**。它实现了 `ISourceCodeAccessor` 接口，让 UE5 编辑器能够：

- 检测系统中是否安装了 CLion
- 从编辑器中的代码引用（如编译错误、断点）直接跳转到 CLion 中对应文件的指定行号
- 打开整个项目（以 CMakeLists.txt 形式）
- 批量打开多个源码文件

**为什么存在？** UE5 默认的源码编辑器是 Visual Studio/VSCode。如果你使用 CLion 作为主力 IDE，这个 plugin 让编辑器的所有"在 IDE 中打开"操作都路由到 CLion，而不是 VS。

## 使用场景

- 你在 Linux/Mac 上使用 CLion 做 UE5 C++ 开发，希望从编辑器双击错误直接跳到 CLion
- 你用 CLion 的 CMake 集成来浏览和编辑 UE5 源码，需要编辑器能正确调起 CLion
- 你的团队统一使用 JetBrains 系工具链（CLion + Rider + Toolbox）

## 蓝图用法

⚠️ 此 plugin **不暴露任何 Blueprint 节点**。它是纯 Editor 工具类 plugin，功能完全在编辑器 UI 层面运作（Preferences → Source Code Editor）。

## C++ 用法

此 plugin 不作为开发依赖使用——它是编辑器内部的 Source Code Accessor 注册模块。普通项目代码不需要直接调用它的 API。

### 工作原理

plugin 在模块启动时通过 `IModularFeatures` 注册自己为 `SourceCodeAccessor`：

```cpp
// CLionSourceCodeAccessModule.cpp
void FCLionSourceCodeAccessModule::StartupModule()
{
    CLionSourceCodeAccessor.RefreshAvailability();
    IModularFeatures::Get().RegisterModularFeature(TEXT("SourceCodeAccessor"), &CLionSourceCodeAccessor);
}
```

编辑器启动后，用户在 **Editor Preferences → General → Source Code** 中选择 "CLion" 作为 Source Code Editor 即可。

### CLion 可执行文件检测逻辑

plugin 会按优先级自动搜索 CLion 安装路径：

**Windows：**
1. JetBrains Toolbox 注册表路径 → 读取 `.settings.json` 中的 `install_location` → 在 `apps/CLion` 下搜索 `clion64.exe`
2. 注册表 `HKCU/HKLM` 中 `clion64.exe` 的 shell open command

**macOS：**
1. `com.jetbrains.CLion-EAP`（EAP 版本优先）
2. `com.jetbrains.CLion`（正式版）
3. 硬编码回退：`/Applications/CLion.app/Contents/MacOS/clion`

**Linux：**
1. `/opt/clion/bin/clion.sh`
2. `/usr/share/applications/jetbrains-clion.desktop`
3. `~/.local/share/applications/jetbrains-clion.desktop`
4. `$PATH` 中包含 "CLion" 的路径下的 `clion.sh`

### 项目文件检测

`DoesSolutionExist()` 检查以下位置是否存在 `CMakeLists.txt`：
1. 项目根目录（`ProjectDir/CMakeLists.txt`）
2. 引擎根目录（`RootDir/CMakeLists.txt`，适用于引擎源码项目）

## Demo 示例

无需代码示例。使用方式：

1. 确保已安装 CLion（通过官方安装器或 JetBrains Toolbox）
2. 生成 UE5 的 CMake 项目文件（`CMakeLists.txt`）
3. 打开 UE5 编辑器 → **Editor Preferences** → **General** → **Source Code**
4. 在 Source Code Editor 下拉菜单中选择 **CLion**
5. 点击编译错误或代码引用 → 自动在 CLion 中打开对应文件和行号

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础功能（路径处理、文件系统、日志等） |
| `SourceCodeAccess` | 源码访问器抽象接口 `ISourceCodeAccessor` |
| `DesktopPlatform` | 平台相关的桌面功能（注册表查询等） |
| `Json` | 解析 JetBrains Toolbox 的 `.settings.json` 配置 |
| `HotReload` | 热重载支持（仅编辑器构建时依赖） |

## 已知限制

- **`AddSourceFiles` 未实现**：返回 `false`，带有一个 `@todo.clion` 注释说明需要手动添加或重新生成项目
- **`SaveAllOpenDocuments` 未实现**：注释中提到 CLion 2017.3 将支持此功能，但代码至今仍返回 `false`
- **不支持 ColumnNumber**：`OpenFileAtLine` 接受列号参数但未使用，只定位到行
- 依赖 `CMakeLists.txt` 存在——如果项目未生成 CMake 文件，`DoesSolutionExist()` 返回 `false`

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da` | IWYU includes 清理 | 无功能性变更，仅减少头文件依赖 |
| 2022-11-07 | `0a10c21` | Engine staging 更新 | 批量同步，非针对性修改 |
| 2022-08-15 | `5d66537` | 添加未分配内存标记 | 内存追踪标签，非功能性变更 |

最近一次**功能性更新**是 2022-03-31 的 `216f515`（在更多位置搜索 CLion 安装路径）。

### 维护评价

- ⚠️ **维护不活跃**：最后一次实质性功能更新在 2022 年 3 月，距今超过 4 年
- 代码中留有多个 `@todo.clion` 标记，从未完成
- `SaveAllOpenDocuments` 的注释提到 "2017.3" 版本支持，但至今未实现
- Plugin 本身功能简单且稳定，不太需要频繁更新
- **建议**：如果你在使用 CLion，可以正常使用此 plugin。但如果有更复杂的需求（如自动同步 CMake 项目），可能需要自定义扩展或使用 JetBrains 官方的 UnrealLink 插件（随 CLion 内置）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/Developer/CLionSourceCodeAccess)
- [ISourceCodeAccessor 接口](https://github.com/EpicGames/UnrealEngine/blob/5.6/Engine/Source/Developer/SourceCodeAccess/Public/ISourceCodeAccessor.h)
- [同系列插件：VS Code Source Code Access](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/Developer/VisualStudioCodeSourceCodeAccess)
- [JetBrains Toolbox](https://www.jetbrains.com/toolbox-app/)
