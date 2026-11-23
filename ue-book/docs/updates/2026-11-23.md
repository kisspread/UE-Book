---
title: '2026-11-23 引擎周报'
date: '2026-11-23'
---
# 2026-11-23 引擎周报

## ✨ 新功能
- Blueprint Graph DSL 与 Toolsets：C++ DSL 成为唯一 Blueprint graph DSL，扩展覆盖 graph 中 agent 会遇到的其余内容；declaration tools 覆盖 My Blueprint 面板和 Class Settings。
- 新增 LiveDebugView 实验性引擎插件，提供 agent-drivable runtime debug views 和 trackers，并以 MCP tools 形式服务。
- ShellToolset 工具抽取到独立的实验性插件。
- IK Retargeter 新增 Python emitter，可通过 script API 重建 IK Rigs 和 IK Retargeters，并支持逐属性比较。
- ShaderAudit 新增 Python API，用于加载 SHK 文件并通过 pandas 查询 shader。
- 新增 Static mesh 到 Skeletal mesh 转换的 Python 和 MCP 访问。
- Chooser Table Editor 增加 row groups。
- LevelToolset 增加对 saved level actors、loaded-only actor search 和 level instance levels 的支持。
- ActorToolset 增加对 editor-only components 和 used materials 的支持。
- 新增 World Partition per-cell streaming 数据在 cook 期间的可选 CSV 导出，由新的 console variable 控制，供下游工具使用。
- UMG WidgetBlueprintEditorSubsystem 新增 Palette 收藏与分类的脚本访问：GetPaletteFavorites、AddPaletteFavorite、RemovePaletteFavorite、Get/SetPaletteCategory，并让对应 UI 控件路由到这些函数。
- WidgetAnimationToolset 新增脚本能力：设置 Widget Material track 的 brush property path，列出 widget animation 的 bindings 及其 widgets，获取/设置 2D transform section 的 active channels。
- Level Sequence audio section 新增“是否重复”的脚本 getter。
- Python Levels/Worlds 暴露 World Partition streaming descriptor 给 Python。
- Smart Objects 和 World Conditions 从 Python 编辑时现在会应用 details panel 所应用的 repairs 和 query compilation，并补充缺失的 script entry points。
- MaterialEditingLibrary 将 VertexColor 及类似节点的未命名 RGB 输出命名为 "RGB"。
- PIE 启动时记录每个新进程的日志文件，并在 dedicated server 进程开始监听时向脚本报告。
- EDA 将 Python interpreter 报告为 sys.executable，并在 execute_python usage text 中加入 level-change 指引。
- Unreal Canvas Bridge 改进：Build Source 在所有引擎上从 Local 路径开始；支持将资产拖放到 3D preview card 上，并且不会覆盖被拖拽文件旁边的同名文件。

## 🚀 重大变更
- UMG 的 WidgetAnimationToolset 插件被 UWidgetBlueprintEditorSubsystem 中的函数替代，相关脚本和集成需要迁移。
- Blueprint Graph DSL 中 C++ DSL 成为唯一 DSL，替代其他实现；declaration tools 相应扩展。
- ShellToolset 移至实验性插件，原有集成方式改变。
- ToolsetRegistry 的 cooked-runtime toolset 支持现在从 AIRuntimeCallable tools 推断，替代手动配置。

## ⚡ 性能优化
- GeometryScript 的 primitive-from-list 函数修复 int32 尺寸溢出和避免无界分配，降低资源风险。
- PythonScriptPlugin 的 Python wrapper type rebuilds 现在持有 GIL，提升并发重建的线程安全性。

## 🐛 Bug 修复
- GeometryScript：修复 CopyBonesFromMesh 在 weighted root bone 及合法但 zero-bone source 下的 fatal checks；修复 ComputeTangents 使用负 UV layer 时的崩溃。
- PythonScriptPlugin：绑定 Python callable 时若 Blueprint 在 bind 期间重新编译，不再读取已释放的 delegate 数据；移除重复的 RebuildGIL 声明。
- Python Levels/Worlds：编辑器替换 level 时释放对 open level package 的 Python 引用。
- IK Retargeter：实验性 op controllers 在 op 消失后拒绝操作、标记 retargeter modified，并通过 ApplySettings 应用设置；脚本 setter 分配 asset reference 时现在咨询 editor 的 asset reference filter，覆盖嵌套引用、op controllers 和 text setters。
- Physics toolsets：加载 PhysicsAssetEditor 后再请求 subsystem，修复从未打开 physics asset 的编辑器中 toolset 不工作的问题。
- 防止 Python 使用 LightWeightInstanceFactory 时崩溃。
- nDisplay：nDisplay Blueprint 在 config factory 外部创建时会获得 factory 的 config setup；通过 config factory 导入 .ndisplay 文件时读取文件而非 assert，且 factory 拥有 .ndisplay 导入；六个 setter 的脚本编辑现在记录用于 undo 和 Multi-User。
- Movie Render Graph：AddLabeledEdge 在成功创建 edge 时返回 true。
- CameraCalibrationCore：当 after-tonemap lens distortion pass 的 material 未解析为 post-process material 时跳过该 pass，而不是断言。
- Mutable：合入 null-dereference 和 pending-update 修复，不包含 scripting refactor。
- Toolset Level：GetFolders 不再在 actor 移动后列出其保存的旧文件夹。
- WidgetAnimationToolset：RemoveWidgetAnimation 现在刷新打开的 Widget Blueprint 编辑器的 Animations 列表。
- PackFactory：加固 .upack 导入，抵御不可信 pack。
- Audio PATT：在编辑器中将 Synesthesia Meter 切换到 Peak 或 TruePeak 时设置 zero attack 和 digital response。
- MetaHuman PATT：ProcessPerformance 保留自定义 mono face models，而不是重置为默认值。
- MVVMToolset：ListBindingConversionOptions 按 binding type 比较 function-backed fields，setter destinations 不再被误报为 unbridgeable；并说明无法比较两个字段的原因。
- UAnimationBlueprintLibrary::AddAnimationNotifyStateEvent 现在会调用 OnAnimNotifyCreatedInEditor。
- ToolsetRegistry：在 baked tool schemas 中记录 $ref、$id、definitions 等 location keyword 错误；PerfToolset 的递归树改内联描述。
- Cheat extension 注册从 CDO constructors 移至 StartupModule/ShutdownModule，并在 module shutdown 时移除扩展。

## 🔧 API 变更
- AssetTools 新增 IAssetTools::FindAssetByObjectPath，可查找 package 已存在磁盘但尚未进入 asset registry 的资产；ToolsetRegistry 的 AssetExists 使用该接口。
- UMG UWidgetBlueprintEditorSubsystem 新增多个 Palette 收藏与分类函数，并替代 WidgetAnimationToolset 插件。
- WidgetAnimationToolset 新增脚本设置 brush property path、列出 bindings、操作 2D transform section active channels 的能力。
- Level Sequence audio section 新增 repeats getter。
- Python Levels/Worlds 暴露 World Partition streaming descriptor。
- ShaderAudit 新增 Python API。
- Smart Objects 和 World Conditions 补充 script entry points。
- MaterialEditingLibrary 将未命名 RGB 输出命名为 "RGB"。

## ⚠️ 废弃预告
- ToolsetRegistry 的 EnableCookedRuntimeSupport 已废弃，cooked-runtime toolset 支持改为从 AIRuntimeCallable tools 自动推断。