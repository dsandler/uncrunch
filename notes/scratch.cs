			case AtlasDataFormat.Packer:
				using (FileStream fileStream2 = File.OpenRead (Path.Combine (Engine.ContentDirectory, path + ".meta"))) {
					BinaryReader binaryReader2 = new BinaryReader (fileStream2);
					binaryReader2.ReadInt32 ();
					binaryReader2.ReadString ();
					binaryReader2.ReadInt32 ();
					short num10 = binaryReader2.ReadInt16 ();
					for (int l = 0; l < num10; l++) {
						string str2 = binaryReader2.ReadString ();
						string path5 = Path.Combine (Path.GetDirectoryName (path), str2 + ".data");
						VirtualTexture virtualTexture4 = VirtualContent.CreateTexture (path5);
						atlas.Sources.Add (virtualTexture4);
						MTexture parent3 = new MTexture (virtualTexture4);
						short num11 = binaryReader2.ReadInt16 ();
						for (int m = 0; m < num11; m++) {
							string text4 = binaryReader2.ReadString ().Replace ('\\', '/');
							short x = binaryReader2.ReadInt16 ();
							short y = binaryReader2.ReadInt16 ();
							short width = binaryReader2.ReadInt16 ();
							short height = binaryReader2.ReadInt16 ();
							short num12 = binaryReader2.ReadInt16 ();
							short num13 = binaryReader2.ReadInt16 ();
							short width2 = binaryReader2.ReadInt16 ();
							short height2 = binaryReader2.ReadInt16 ();
							atlas.textures [text4] = new MTexture (parent3, text4, new Rectangle (x, y, width, height), new Vector2 ((float)(-num12), (float)(-num13)), width2, height2);
						}
					}
					if (fileStream2.Position < fileStream2.Length) {
						string a2 = binaryReader2.ReadString ();
						if (a2 == "LINKS") {
							short num14 = binaryReader2.ReadInt16 ();
							for (int n = 0; n < num14; n++) {
								string key2 = binaryReader2.ReadString ();
								string value2 = binaryReader2.ReadString ();
								atlas.links.Add (key2, value2);
							}
						}
					}
				}
				break;
			case AtlasDataFormat.PackerNoAtlas:
				using (FileStream fileStream = File.OpenRead (Path.Combine (Engine.ContentDirectory, path + ".meta"))) {
					BinaryReader binaryReader = new BinaryReader (fileStream);
					binaryReader.ReadInt32 ();
					binaryReader.ReadString ();
					binaryReader.ReadInt32 ();
					short num = binaryReader.ReadInt16 ();
					for (int i = 0; i < num; i++) {
						string path3 = binaryReader.ReadString ();
						string path4 = Path.Combine (Path.GetDirectoryName (path), path3);
						short num2 = binaryReader.ReadInt16 ();
						for (int j = 0; j < num2; j++) {
							string text3 = binaryReader.ReadString ().Replace ('\\', '/');
							short num3 = binaryReader.ReadInt16 ();
							short num4 = binaryReader.ReadInt16 ();
							short num5 = binaryReader.ReadInt16 ();
							short num6 = binaryReader.ReadInt16 ();
							short num7 = binaryReader.ReadInt16 ();
							short num8 = binaryReader.ReadInt16 ();
							short frameWidth = binaryReader.ReadInt16 ();
							short frameHeight = binaryReader.ReadInt16 ();
							VirtualTexture virtualTexture3 = VirtualContent.CreateTexture (Path.Combine (path4, text3 + ".data"));
							atlas.Sources.Add (virtualTexture3);
							atlas.textures [text3] = new MTexture (virtualTexture3, new Vector2 ((float)(-num7), (float)(-num8)), frameWidth, frameHeight);
							atlas.textures [text3].AtlasPath = text3;
						}
					}
					if (fileStream.Position < fileStream.Length) {
						string a = binaryReader.ReadString ();
						if (a == "LINKS") {
							short num9 = binaryReader.ReadInt16 ();
							for (int k = 0; k < num9; k++) {
								string key = binaryReader.ReadString ();
								string value = binaryReader.ReadString ();
								atlas.links.Add (key, value);
							}
						}
					}
				}
				break;



        VirtualTexture:

					string path = System.IO.Path.Combine (Engine.ContentDirectory, this.Path);
					using (FileStream fileStream = File.OpenRead (path)) {
						fileStream.Read (VirtualTexture.bytes, 0, 524288);
						int num = 0;
						int num2 = BitConverter.ToInt32 (VirtualTexture.bytes, num);
						int num3 = BitConverter.ToInt32 (VirtualTexture.bytes, num + 4);
						bool flag = VirtualTexture.bytes [num + 8] == 1;
						num += 9;
						int num4 = num2 * num3 * 4;
						int num5 = 0;
						try {
							byte[] array4 = VirtualTexture.bytes;
							fixed (byte[] array5 = array4) {
								byte* ptr2 = (byte*)(long)((array4 != null && array5.Length != 0) ? ((IntPtr)(&array5 [0])) : ((IntPtr)(void*)null));
								byte[] array6 = VirtualTexture.buffer;
								fixed (byte[] array7 = array6) {
									byte* ptr3 = (byte*)(long)((array6 != null && array7.Length != 0) ? ((IntPtr)(&array7 [0])) : ((IntPtr)(void*)null));
									while (num5 < num4) {
										int num6 = ptr2 [num] * 4;
										if (flag) {
											byte b = ptr2 [num + 1];
											if (b > 0) {
												ptr3 [num5] = ptr2 [num + 4];
												ptr3 [num5 + 1] = ptr2 [num + 3];
												ptr3 [num5 + 2] = ptr2 [num + 2];
												ptr3 [num5 + 3] = b;
												num += 5;
											} else {
												ptr3 [num5] = 0;
												ptr3 [num5 + 1] = 0;
												ptr3 [num5 + 2] = 0;
												ptr3 [num5 + 3] = 0;
												num += 2;
											}
										} else {
											ptr3 [num5] = ptr2 [num + 3];
											ptr3 [num5 + 1] = ptr2 [num + 2];
											ptr3 [num5 + 2] = ptr2 [num + 1];
											ptr3 [num5 + 3] = 255;
											num += 4;
										}
										if (num6 > 4) {
											int j = num5 + 4;
											for (int num7 = num5 + num6; j < num7; j += 4) {
												ptr3 [j] = ptr3 [num5];
												ptr3 [j + 1] = ptr3 [num5 + 1];
												ptr3 [j + 2] = ptr3 [num5 + 2];
												ptr3 [j + 3] = ptr3 [num5 + 3];
											}
										}
										num5 += num6;
										if (num > 524256) {
											int num8 = 524288 - num;
											for (int k = 0; k < num8; k++) {
												ptr2 [k] = ptr2 [num + k];
											}
											fileStream.Read (VirtualTexture.bytes, num8, 524288 - num8);
											num = 0;
										}
									}
								}
							}
						} finally {
							array5 = null;
							array7 = null;
						}
						this.Texture = new Texture2D (Engine.Graphics.GraphicsDevice, num2, num3);
						this.Texture.SetData (VirtualTexture.buffer, 0, num4);
					}
        
