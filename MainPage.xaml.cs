using System.Diagnostics;
using CommunityToolkit.Maui.Storage;

namespace metarapp;

public partial class MainPage : ContentPage
{
    private string _arquivoSBVT = string.Empty;
    private string _arquivoINMET = string.Empty;
    private List<string> _arquivosUpperAir = new();
    private string _pastaDestino = string.Empty;

    public MainPage()
    {
        InitializeComponent();
        AtualizarInterface();
    }

    private void AtualizarInterface()
    {
        // Atualiza labels com os arquivos selecionados
        LblArquivoSBVT.Text = string.IsNullOrEmpty(_arquivoSBVT)
            ? "❌ Nenhum arquivo SBVT selecionado"
            : $"✅ {Path.GetFileName(_arquivoSBVT)}";

        LblArquivoINMET.Text = string.IsNullOrEmpty(_arquivoINMET)
            ? "❌ Nenhum arquivo INMET selecionado"
            : $"✅ {Path.GetFileName(_arquivoINMET)}";

        LblArquivoUpperAir.Text = _arquivosUpperAir.Count == 0
            ? "❌ Nenhum arquivo UpperAir selecionado"
            : $"✅ {_arquivosUpperAir.Count} arquivo(s) UpperAir selecionado(s)";

        // Habilita botão processar apenas se todos os arquivos e pasta estiverem selecionados
        BtnProcessar.IsEnabled = !string.IsNullOrEmpty(_arquivoSBVT)
                                && !string.IsNullOrEmpty(_arquivoINMET)
                                && _arquivosUpperAir.Count > 0
                                && !string.IsNullOrEmpty(_pastaDestino);
    }

    private async void BtnSelecionarSBVT_Clicked(object sender, EventArgs e)
    {
        try
        {
            var resultado = await FilePicker.Default.PickAsync(new PickOptions
            {
                PickerTitle = "Selecione o arquivo SBVT.csv",
                FileTypes = new FilePickerFileType(new Dictionary<DevicePlatform, IEnumerable<string>>
                {
                    { DevicePlatform.WinUI, new[] { ".csv" } },
                    { DevicePlatform.MacCatalyst, new[] { "csv" } },
                })
            });

            if (resultado != null)
            {
                _arquivoSBVT = resultado.FullPath;
                AtualizarInterface();
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert("Erro", $"Erro ao selecionar arquivo SBVT: {ex.Message}", "OK");
        }
    }

    private async void BtnSelecionarINMET_Clicked(object sender, EventArgs e)
    {
        try
        {
            var resultado = await FilePicker.Default.PickAsync(new PickOptions
            {
                PickerTitle = "Selecione o arquivo INMET (dados_A612_H_...)",
                FileTypes = new FilePickerFileType(new Dictionary<DevicePlatform, IEnumerable<string>>
                {
                    { DevicePlatform.WinUI, new[] { ".csv" } },
                    { DevicePlatform.MacCatalyst, new[] { "csv" } },
                })
            });

            if (resultado != null)
            {
                _arquivoINMET = resultado.FullPath;
                AtualizarInterface();
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert("Erro", $"Erro ao selecionar arquivo INMET: {ex.Message}", "OK");
        }
    }

    private async void BtnSelecionarUpperAir_Clicked(object sender, EventArgs e)
    {
        try
        {
            var resultados = await FilePicker.Default.PickMultipleAsync(new PickOptions
            {
                PickerTitle = "Selecione arquivo(s) UpperAir (.grib2.nc)",
                FileTypes = new FilePickerFileType(new Dictionary<DevicePlatform, IEnumerable<string>>
                {
                    { DevicePlatform.WinUI, new[] { ".nc" } },
                    { DevicePlatform.MacCatalyst, new[] { "nc" } },
                })
            });

            if (resultados != null && resultados.Count() > 0)
            {
                _arquivosUpperAir = resultados.Select(f => f.FullPath).ToList();
                AtualizarInterface();
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert("Erro", $"Erro ao selecionar arquivo(s) UpperAir: {ex.Message}", "OK");
        }
    }

    private async void BtnSelecionarDestino_Clicked(object sender, EventArgs e)
    {
        try
        {
            var result = await FolderPicker.Default.PickAsync(default);

            if (result.IsSuccessful)
            {
                _pastaDestino = result.Folder.Path;
                LblDestino.Text = $"📁 {_pastaDestino}";
                LblDestino.TextColor = Colors.DarkGreen;
                AtualizarInterface();
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert("Erro", $"Erro ao selecionar pasta: {ex.Message}", "OK");
        }
    }

    private void BtnLimpar_Clicked(object sender, EventArgs e)
    {
        _arquivoSBVT = string.Empty;
        _arquivoINMET = string.Empty;
        _arquivosUpperAir.Clear();
        _pastaDestino = string.Empty;
        LblDestino.Text = "Nenhuma pasta selecionada";
        LblDestino.TextColor = Colors.Gray;
        LblStatus.Text = "Aguardando processamento...";
        LblStatus.TextColor = Colors.Gray;
        AtualizarInterface();
    }

    private async void BtnProcessar_Clicked(object sender, EventArgs e)
    {
        if (string.IsNullOrEmpty(_arquivoSBVT))
        {
            await DisplayAlert("Aviso", "Selecione o arquivo SBVT.csv", "OK");
            return;
        }

        if (string.IsNullOrEmpty(_arquivoINMET))
        {
            await DisplayAlert("Aviso", "Selecione o arquivo INMET (dados_A612_H_...)", "OK");
            return;
        }

        if (_arquivosUpperAir.Count == 0)
        {
            await DisplayAlert("Aviso", "Selecione pelo menos 1 arquivo UpperAir (.grib2.nc)", "OK");
            return;
        }

        if (string.IsNullOrEmpty(_pastaDestino))
        {
            await DisplayAlert("Aviso", "Selecione uma pasta de destino.", "OK");
            return;
        }

        // Desabilita todos os botões durante o processamento
        BtnProcessar.IsEnabled = false;
        BtnSelecionarSBVT.IsEnabled = false;
        BtnSelecionarINMET.IsEnabled = false;
        BtnSelecionarUpperAir.IsEnabled = false;
        BtnSelecionarDestino.IsEnabled = false;
        BtnLimpar.IsEnabled = false;

        LblStatus.Text = "⏳ Processando arquivos...";
        LblStatus.TextColor = Colors.DarkOrange;

        try
        {
            await RodarPython(_arquivoSBVT, _arquivoINMET, _arquivosUpperAir, _pastaDestino);

            LblStatus.Text = "✅ Processamento concluído com sucesso!";
            LblStatus.TextColor = Colors.DarkGreen;

            // DEPOIS ✅
            await DisplayAlert("Sucesso", $"Arquivos CALPUFF gerados com sucesso!\n\n✅ radiacao_tratada.csv\n✅ teste2.csv\n✅ upperair_tratado.csv\n✅ UpperAir_2024_Gerado.DAT", "OK");

        }
        catch (Exception ex)
        {
            LblStatus.Text = "❌ Erro no processamento.";
            LblStatus.TextColor = Colors.DarkRed;
            
            // ⚠️ MODO DEBUG TEMPORÁRIO: Mostra erro completo
            await DisplayAlert("🐛 DEBUG - Erro Detalhado", ex.Message, "OK");
        }
        finally
        {
            // Reabilita os botões
            BtnProcessar.IsEnabled = true;
            BtnSelecionarSBVT.IsEnabled = true;
            BtnSelecionarINMET.IsEnabled = true;
            BtnSelecionarUpperAir.IsEnabled = true;
            BtnSelecionarDestino.IsEnabled = true;
            BtnLimpar.IsEnabled = true;
        }
    }

    // ⚠️⚠️⚠️ MODO DEBUG TEMPORÁRIO - VOLTAR DEPOIS ⚠️⚠️⚠️
    private async Task RodarPython(string caminhoSBVT, string caminhoINMET, List<string> caminhos_upperair, string pastaDestino)
    {
        string caminhoPython = "python";
        string caminhoScript = Path.Combine(AppContext.BaseDirectory, "script.py");

        if (!File.Exists(caminhoScript))
        {
            throw new FileNotFoundException(
                $"❌ script.py NÃO ENCONTRADO:\n{caminhoScript}\n\n" +
                $"BaseDirectory atual:\n{AppContext.BaseDirectory}");
        }

        // Junta múltiplos caminhos com ;
        string upperair_args = string.Join(";", caminhos_upperair);

        var psi = new ProcessStartInfo
        {
            FileName = caminhoPython,
            Arguments = $"\"{caminhoScript}\" \"{caminhoSBVT}\" \"{caminhoINMET}\" \"{upperair_args}\" \"{pastaDestino}\"",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = false,  // ✅ TEMPORÁRIO: Mostra janela Python
            WorkingDirectory = AppContext.BaseDirectory
        };

        Debug.WriteLine("========================================");
        Debug.WriteLine("🐍 EXECUTANDO PYTHON:");
        Debug.WriteLine($"Comando: {caminhoPython}");
        Debug.WriteLine($"Args: {psi.Arguments}");
        Debug.WriteLine($"WorkDir: {psi.WorkingDirectory}");
        Debug.WriteLine("========================================");

        using var proc = Process.Start(psi)
            ?? throw new Exception("❌ Python NÃO iniciou. Verifique:\n\n" +
                "1. Python instalado? Digite no CMD: python --version\n" +
                "2. Python no PATH?\n" +
                "3. Script.py existe?");

        string saida = await proc.StandardOutput.ReadToEndAsync();
        string erro = await proc.StandardError.ReadToEndAsync();

        await proc.WaitForExitAsync();

        // ✅ LOG COMPLETO no VS Code Output > Debug
        Debug.WriteLine("\n========== PYTHON STDOUT ==========");
        Debug.WriteLine(string.IsNullOrWhiteSpace(saida) ? "(vazio)" : saida);
        Debug.WriteLine("===================================\n");

        Debug.WriteLine("========== PYTHON STDERR ==========");
        Debug.WriteLine(string.IsNullOrWhiteSpace(erro) ? "(vazio)" : erro);
        Debug.WriteLine("===================================\n");

        Debug.WriteLine($"🔢 ExitCode: {proc.ExitCode}");

        if (proc.ExitCode != 0)
        {
            // ⚠️ TEMPORÁRIO: Mostra TUDO na tela
            string mensagemCompleta = 
                $"❌ ERRO PYTHON (ExitCode: {proc.ExitCode})\n\n" +
                $"📂 Arquivos:\n" +
                $"  SBVT: {Path.GetFileName(caminhoSBVT)}\n" +
                $"  INMET: {Path.GetFileName(caminhoINMET)}\n" +
                $"  UpperAir: {caminhos_upperair.Count} arquivo(s)\n" +
                $"  Destino: {pastaDestino}\n\n" +
                $"📋 STDERR:\n{(string.IsNullOrWhiteSpace(erro) ? "(sem erros stderr)" : erro)}\n\n" +
                $"📋 STDOUT:\n{(string.IsNullOrWhiteSpace(saida) ? "(sem saída)" : saida)}";
            
            throw new Exception(mensagemCompleta);
        }

        // Sucesso!
        Debug.WriteLine("✅ Python executou com sucesso!");
    }
    // ⚠️⚠️⚠️ FIM MODO DEBUG - LEMBRAR DE REVERTER ⚠️⚠️⚠️
}
